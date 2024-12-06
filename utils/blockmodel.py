from pprint import pformat
import pandas as pd
import numpy as np


class BlockModelHandler:
    def __init__(self, bm, filter_condition=None, compact=False) -> None:
        self.bm = bm
        self.filter = filter_condition
        self.is_compact = compact
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
    

    def set_color(self, grade):
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
    
    def make_compact(self):
        self._bm_dataframe['i_index'] = self._bm_dataframe['i_index'].astype(int)
        self._bm_dataframe['j_index'] = self._bm_dataframe['j_index'].astype(int)
        self._bm_dataframe['k_index'] = self._bm_dataframe['k_index'].astype(int)

        if self.filter:
            self._bm_dataframe['is_outer'] = False
            grouped = self._bm_dataframe.groupby(['j_index', 'k_index'])
            
            # Iterate through groups
            for (j, k), group in grouped:
                min_i, max_i = group['i_index'].min(), group['i_index'].max()
                self._bm_dataframe.loc[group.index, 'is_outer'] |= (group['i_index'] == min_i) | (group['i_index'] == max_i)

            # Repeat the process for j_index grouped by i_index and k_index
            grouped = self._bm_dataframe.groupby(['i_index', 'k_index'])
            for (i, k), group in grouped:
                min_j, max_j = group['j_index'].min(), group['j_index'].max()
                self._bm_dataframe.loc[group.index, 'is_outer'] |= (group['j_index'] == min_j) | (group['j_index'] == max_j)

            # Repeat the process for k_index grouped by i_index and j_index
            grouped = self._bm_dataframe.groupby(['i_index', 'j_index'])
            for (i, j), group in grouped:
                min_k, max_k = group['k_index'].min(), group['k_index'].max()
                self._bm_dataframe.loc[group.index, 'is_outer'] |= (group['k_index'] == min_k) | (group['k_index'] == max_k)
        else:
            min_i, max_i = 0, len(self.bm.tensor_u)
            min_j, max_j = 0, len(self.bm.tensor_v)
            min_k, max_k = 0, len(self.bm.tensor_w)

            # Check if each block is on the boundary along any axis
            is_outer_i = (self._bm_dataframe['i_index'] == min_i) | (self._bm_dataframe['i_index'] == max_i)
            is_outer_j = (self._bm_dataframe['j_index'] == min_j) | (self._bm_dataframe['j_index'] == max_j)
            is_outer_k = (self._bm_dataframe['k_index'] == min_k) | (self._bm_dataframe['k_index'] == max_k)

            # Combine conditions
            self._bm_dataframe['is_outer'] = is_outer_i | is_outer_j | is_outer_k


    def _bm_to_pandas_dataframe(self):
        origin = np.array(self.get_bm_origin)
        rows = []
        x_cumsum = np.cumsum(np.insert(self.bm.tensor_u, 0, 0))[:-1] + origin[0]
        y_cumsum = np.cumsum(np.insert(self.bm.tensor_v, 0, 0))[:-1] + origin[1]
        z_cumsum = np.cumsum(np.insert(self.bm.tensor_w, 0, 0))[:-1] + origin[2]
        for i, x in enumerate(self.bm.tensor_u):
            for j, y in enumerate(self.bm.tensor_v):
                for k, z in enumerate(self.bm.tensor_w):
                    rows.append({
                        'x_size': x, 'y_size': y, 'z_size': z,
                        'x_coord': x_cumsum[i], 'y_coord': y_cumsum[j], 'z_coord': z_cumsum[k],
                        'i_index': i,
                        'j_index': j,
                        'k_index': k,
                        'bench': str(int(z_cumsum[k]))
                    })

        df = pd.DataFrame(rows)

        for attribute in self._get_attribute_list:
            for key, value in attribute.items():
                df[key] = value.flatten(order="F")

        if self.filter:
            return df.query(self._filter_query_string)
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
    def get_bm_extends(self) -> dict:
        bm_extends = dict()
        bm_extends["min_x"] = self._bm_dataframe["x_coord"].min()
        bm_extends["max_x"] = self._bm_dataframe["x_coord"].max()
        bm_extends["min_y"] = self._bm_dataframe["y_coord"].min()
        bm_extends["mid_x"] = self._bm_dataframe["x_coord"].median()
        bm_extends["max_y"] = self._bm_dataframe["y_coord"].max()
        bm_extends["mid_y"] = self._bm_dataframe["y_coord"].median()
        bm_extends["min_z"] = self._bm_dataframe["z_coord"].min()
        bm_extends["max_z"] = self._bm_dataframe["z_coord"].max()
        bm_extends["mid_z"] = self._bm_dataframe["z_coord"].median()
        return bm_extends
