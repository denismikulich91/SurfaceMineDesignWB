from pprint import pformat
import pandas as pd
from pandas import DataFrame
import numpy as np
pd.options.mode.copy_on_write = True

class BlockModelHandler:
    def __init__(self, bm) -> None:
        self.bm = bm
        self.name = bm.name
        self._bm_dataframe = self._bm_to_pandas_dataframe()

    def __str__(self):
        return "\nBlock model info:\n\n" + \
            f'Instance of {__class__.__name__}\n' + \
            pformat(self.get_bm_info, depth=3, indent=1, compact=True, width=250)

    @property
    def get_bm_attributes_list(self) -> list:
        return [attr.name for attr in self.bm.attributes]

    @property
    def get_bm_info(self):
        return self.bm.serialize()

    @property
    def get_bm_origin(self):
        return self.get_bm_info.get("center", self.bm.origin)
    
    def filter_dataframe_using_query(self, query: str):
        return self._bm_dataframe.query(query)
    

    @staticmethod
    def set_color(grade):
        if grade < 2.5:
            color = (0, 0, 255)
        elif grade < 3:
            color = (0, 125, 255)
        elif grade < 3.5:
            color = (0, 255, 125)
        elif grade < 4:
            color = (255, 255, 0)
        elif grade < 4.5:
            color = (255, 125, 0)
        else:
            color = (255, 0, 0)
        return color
    
    @staticmethod
    def mark_outer_faces(df: pd.DataFrame):
        # Ensure indices are integers
        df['i_index'] = df['i_index'].astype(int)
        df['j_index'] = df['j_index'].astype(int)
        df['k_index'] = df['k_index'].astype(int)

        index_set = set(zip(df['i_index'], df['j_index'], df['k_index']))

        # Initialize the new column with empty lists
        df['outer_faces'] = [[] for _ in range(len(df))]

        for idx, row in df.iterrows():
            i, j, k = row['i_index'], row['j_index'], row['k_index']

            # Define directions and neighbors
            directions = {
                '-x': (i - 1, j, k),
                '+x': (i + 1, j, k),
                '-y': (i, j - 1, k),
                '+y': (i, j + 1, k),
                '-z': (i, j, k - 1),
                '+z': (i, j, k + 1),
            }
            face_codes = {'-x': 1, '+x': 2, '-y': 3, '+y': 4, '-z': 5, '+z': 6}

            # Check neighbors and mark exposed faces
            exposed_faces = [
                face_codes[face] for face, neighbor in directions.items()
                if neighbor not in index_set
            ]

            df.at[idx, 'outer_faces'] = exposed_faces
    
    @staticmethod
    def make_compact_filtered_model(df: DataFrame):
        # Ensure i, j, k indices are integers
        df['i_index'] = df['i_index'].astype(int)
        df['j_index'] = df['j_index'].astype(int)
        df['k_index'] = df['k_index'].astype(int)

        df['is_outer'] = False
        index_set = set(zip(df['i_index'], df['j_index'], df['k_index']))

        for idx, row in df.iterrows():
            i, j, k = row['i_index'], row['j_index'], row['k_index']

            neighbors = [
                (i - 1, j, k), (i + 1, j, k),  # Neighbors along the i-axis
                (i, j - 1, k), (i, j + 1, k),  # Neighbors along the j-axis
                (i, j, k - 1), (i, j, k + 1),  # Neighbors along the k-axis
            ]
            is_outer = not all(neighbor in index_set for neighbor in neighbors)
            df.at[idx, 'is_outer'] = is_outer


    def _bm_to_pandas_dataframe(self):
        origin = np.array(self.get_bm_origin)
        rows = []
        x_cumsum = np.cumsum(np.insert(self.bm.tensor_u, 0, 0))[:-1] + origin[0]
        y_cumsum = np.cumsum(np.insert(self.bm.tensor_v, 0, 0))[:-1] + origin[1]
        z_cumsum = np.cumsum(np.insert(self.bm.tensor_w, 0, 0))[:-1] + origin[2]
        
        for k, z in enumerate(self.bm.tensor_w):
            for j, y in enumerate(self.bm.tensor_v):
                for i, x in enumerate(self.bm.tensor_u):
                    rows.append({
                        'x_size': x, 'y_size': y, 'z_size': z,
                        'x_coord': x_cumsum[i], 'y_coord': y_cumsum[j], 'z_coord': z_cumsum[k],
                        'i_index': i,
                        'j_index': j,
                        'k_index': k,
                        'color': (120, 120, 120),
                        'bench': str(int(z_cumsum[k]))
                    })

        df = pd.DataFrame(rows)

        for attribute in self._get_attribute_list:
            for key, value in attribute.items():
                df[key] = value.flatten(order="F")

        return df

    @property
    def _filter_query_string(self):
        # example: {'CU_pct': ['>=', 2.4], 'rocktype': ['!=', 'air']}
        query_string = ""
        for i, (column, condition) in enumerate(self.filter.items()):
            operator = condition[0]
            value = condition[1]
            if i > 0:
                query_string += " and "
            query_string += f"{column} {operator} {value}"
        return query_string

    @property
    def _get_attribute_list(self):
        bm_attribute_list = []
        for attribute in self.bm.attributes:
            bm_attribute_list.append({attribute.name: attribute.array.array})
        return bm_attribute_list

    @property
    def get_bm_dataframe(self):
        return self._bm_dataframe
    
    @property
    def get_tensors_length(self):
        return (len(self.bm.tensor_u), len(self.bm.tensor_v), len(self.bm.tensor_w))

    @staticmethod
    def get_bm_extends(bm_df) -> dict:
        bm_extends = dict()
        bm_extends["min_x"] = bm_df["x_coord"].min()
        bm_extends["max_x"] = bm_df["x_coord"].max()
        bm_extends["min_y"] = bm_df["y_coord"].min()
        bm_extends["mid_x"] = bm_df["x_coord"].median()
        bm_extends["max_y"] = bm_df["y_coord"].max()
        bm_extends["mid_y"] = bm_df["y_coord"].median()
        bm_extends["min_z"] = bm_df["z_coord"].min()
        bm_extends["max_z"] = bm_df["z_coord"].max()
        bm_extends["mid_z"] = bm_df["z_coord"].median()
        return bm_extends
