#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import sys
import os.path

from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal

import vtk
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class VTKFrame(QtGui.QFrame):
    def __init__(self, parent = None):
        super(VTKFrame, self).__init__(parent)

        self.vtkWidget = QVTKRenderWindowInteractor(self)
        vl = QtGui.QVBoxLayout(self)
        vl.addWidget(self.vtkWidget)
        vl.setContentsMargins(0, 0, 0, 0)
 
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 
        # Create source
        #Setup the coordinates of eight points
        #(the two faces must be in counter clockwise order as viewd from the outside)
        P0 = [0.0, 0.0, 0.0];
        P1 = [1.0, 0.0, 0.0];
        P2 = [1.0, 1.0, 0.0];
        P3 = [0.0, 1.0, 0.0];
        P4 = [0.0, 0.0, 1.0];
        P5 = [1.0, 0.0, 1.0];
        P6 = [1.0, 1.0, 1.0];
        P7 = [0.0, 1.0, 1.0];
         
         
        #Create the points
        points = vtk.vtkPoints();
        points.InsertNextPoint(P0);
        points.InsertNextPoint(P1);
        points.InsertNextPoint(P2);
        points.InsertNextPoint(P3);
        points.InsertNextPoint(P4);
        points.InsertNextPoint(P5);
        points.InsertNextPoint(P6);
        points.InsertNextPoint(P7);
         
        #Create a hexahedron from the points
        hexa = vtk.vtkHexahedron();
        hexa.GetPointIds().SetId(0,0);
        hexa.GetPointIds().SetId(1,1);
        hexa.GetPointIds().SetId(2,2);
        hexa.GetPointIds().SetId(3,3);
        hexa.GetPointIds().SetId(4,4);
        hexa.GetPointIds().SetId(5,5);
        hexa.GetPointIds().SetId(6,6);
        hexa.GetPointIds().SetId(7,7);
         
        #Add the hexahedron to a cell array
        hexs = vtk.vtkCellArray();
        hexs.InsertNextCell(hexa);
         
        #Add the points and hexahedron to an unstructured grid
        uGrid =vtk.vtkUnstructuredGrid();
        uGrid.SetPoints(points);
        uGrid.InsertNextCell(hexa.GetCellType(), hexa.GetPointIds());
         
        surface=vtk.vtkDataSetSurfaceFilter()
        surface.SetInput(uGrid)
        surface.Update()
         
        aBeamMapper = vtk.vtkDataSetMapper()
        aBeamMapper.SetInput(surface.GetOutput())
        #aBeamMapper.SetInput(uGrid)
        aBeamActor = vtk.vtkActor()
        aBeamActor.SetMapper(aBeamMapper)
        aBeamActor.AddPosition(0,0,0)
        aBeamActor.GetProperty().SetColor(1,1,0)
        aBeamActor.GetProperty().SetOpacity(0.60)
        aBeamActor.GetProperty().EdgeVisibilityOn()
        aBeamActor.GetProperty().SetEdgeColor(1,1,1)
        aBeamActor.GetProperty().SetLineWidth(1.5)
         
        #create a plane to cut,here it cuts in the XZ direction (xz normal=(1,0,0);XY =(0,0,1),YZ =(0,1,0)
        plane=vtk.vtkPlane()
        plane.SetOrigin(0.5,0,0)
        plane.SetNormal(1,0,0)
         
        #create cutter
        cutter=vtk.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInput(aBeamActor.GetMapper().GetInput())
        cutter.Update()
        cutterMapper=vtk.vtkDataSetMapper()
        cutterMapper.SetInputConnection( cutter.GetOutputPort())
         
        #create plane actor
        planeActor=vtk.vtkActor()
        planeActor.GetProperty().SetColor(1,0.5,0.5)
        planeActor.GetProperty().SetLineWidth(2)
        planeActor.SetMapper(cutterMapper)
         
        #Add the actor to the scene
        self.ren.AddActor(aBeamActor)
        self.ren.AddActor(planeActor)
        self.ren.ResetCamera()

        self._initialized = False

    def showEvent(self, evt):
        if not self._initialized:
            self.iren.Initialize()
            self.startTimer(30)
            self._initialized = True

    def timerEvent(self, evt):
        self.ren.GetActiveCamera().Azimuth(1)
        self.vtkWidget.GetRenderWindow().Render()
 
class MainPage(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(MainPage, self).__init__(parent)
        self.setCentralWidget(VTKFrame())

        self.setWindowTitle("Data surface example")

    def categories(self):
        return ['Simple', 'Cutter']

    def mainClasses(self):
        return ['vtkPoints', 'vtkHexahedron', 'vtkCellArray', 'vtkCutter', 'vtkDataSetSurfaceFilter', 'vtkUnstructuredGrid', 'vtkPlane']

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = MainPage()
    w.show()
    sys.exit(app.exec_())
