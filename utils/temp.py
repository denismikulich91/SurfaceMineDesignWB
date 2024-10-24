import FreeCAD as App
import Mesh
import Part

skin_list = App.ActiveDocument.getObjectsByLabel("skin")
skin = skin_list[0]
skin = skin.Mesh
elevation = 400100.0
skin_bb = skin.BoundBox
min_x, min_y, max_x, max_y = skin_bb.XMin, skin_bb.YMin, skin_bb.XMax, skin_bb.YMax
print(min_x, max_x)
p1 = App.Vector(min_x, min_y, elevation)
p2 = App.Vector(min_x, max_y, elevation)
p3 = App.Vector(max_x, max_y, elevation)

p4 = App.Vector(min_x, min_y, elevation)
p5 = App.Vector(max_x, max_y, elevation)
p6 = App.Vector(max_x, min_y, elevation)

plane = Mesh.Mesh([[p1, p2, p3], [p4, p5, p6]])
Mesh.show(plane)
loops = plane.section(skin)
print(len(loops))
Part.show(Part.makePolygon(loops[0]))
