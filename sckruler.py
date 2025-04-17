#17/04/2025 by Sercan Cikintoglu

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMenu, QAction, QActionGroup, QShortcut
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QCursor, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
import sys
import numpy as np

#TODO: stick the cursor to the edge
#TODO: icon

class ScreenRuler(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SckRuler")
        self.setGeometry(300, 300, 600, 60)
        self.setMinimumSize(300, 60)        
        self.setMaximumSize(self.maximumWidth(), 60)        

        # Frameless and on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.margin = 8 #margin for th resizer
 
        self.setMouseTracking(True)
        # Enable dragging
        self._drag_active = False
        self._drag_position = None
        # Enable resizing
        self._resize_active = False
        self._resizePos = None
        self.resizeevent = self.resizeRight
 
        self.is_vertical = False  # Track rotation state
          
          
        #Unit action group  
        self.unit       = "Pixels"
        self.unitshorts = {'Pixels':'px', 'Centimeters':'cm', 'Inches':'in'}        

        self.colors_bg      = {'Orange':"#FFA500", 'Gray':"gray", 'Black':"black", 'Red':"#CC0000", 'White':"white"}
        self.colors_markers = {'Orange':"black",   'Gray':"black",'Black':"white", 'Red':"#FFA500", 'White':"black"}
        self.current_color  = 'Orange'

        self.unit_group = QActionGroup(self)
        self.unit_group.setExclusive(True)

        self.unit2px_action = QAction("Pixels", self, checkable=True)
        self.unit2cm_action = QAction("Centimeters", self, checkable=True)
        self.unit2in_action = QAction("Inches", self, checkable=True)

        self.unit_group.addAction(self.unit2px_action)
        self.unit_group.addAction(self.unit2cm_action)
        self.unit_group.addAction(self.unit2in_action)
        
        self.unit2px_action.setChecked(True) # Set default checked item
                
        self.unit2px_action.triggered.connect(lambda: self.change_unit("Pixels"))
        self.unit2cm_action.triggered.connect(lambda: self.change_unit("Centimeters"))
        self.unit2in_action.triggered.connect(lambda: self.change_unit("Inches"))                

        self.nexttheme_action = QAction("Change Theme",self)
        self.nexttheme_action.setShortcut("C")
        self.nexttheme_action.triggered.connect(self.change_theme)        
        self.addAction(self.nexttheme_action)
#    
        QShortcut(QKeySequence("N"), self, activated=self.nextunit)
 
        #Rotate action 
        self.rotate_action = QAction("Rotate",self)
        self.rotate_action.setShortcut("R")
        self.rotate_action.triggered.connect(self.toggle_orientation)        
        self.addAction(self.rotate_action)

        #Transparent action
        self.transparent_action = QAction("Transparent", self, checkable=True)
        self.transparent_action.setShortcut("T")        
        self.transparent_action.setChecked(False)
        self.transparent_action.triggered.connect(self.update)
        self.addAction(self.transparent_action)

        #Close action
        self.close_action = QAction("Close",self)
        self.close_action.setShortcut("Q")
        self.close_action.triggered.connect(self.close)        
        self.addAction(self.close_action)


      
    def contextMenuEvent(self,event):
       context_menu = QMenu(self)
#       context_menu .setStyleSheet("QMenu { color: "+self.colors_markers[self.current_color]+"; }")
#       context_menu .setStyleSheet("QMenu::item:selected {background-color: 

       context_menu.addAction(self.unit2px_action)
       context_menu.addAction(self.unit2cm_action)
       context_menu.addAction(self.unit2in_action) 
       context_menu.addSeparator()
       
       context_menu.addAction(self.rotate_action)
       context_menu.addSeparator()
       context_menu.addAction(self.transparent_action)
       context_menu.addSeparator()              
       context_menu.addAction(self.nexttheme_action)
       context_menu.addSeparator()       
       context_menu.addAction(self.close_action)

       action = context_menu.exec(self.mapToGlobal(event.pos())) 
       
#       if action == close_act:
#         self.close()     


    def toggle_orientation(self):     
         self.is_vertical = not self.is_vertical
         
         if self.is_vertical:
           self.setMinimumSize(0, 0)       
           self.setMaximumSize(self.maximumWidth(),self.maximumWidth())           
           self.setGeometry(self.x(), self.y(), 60, self.width()) # Swap width & height
           self.setMinimumSize(60, 300)       
           self.setMaximumSize(60,self.maximumWidth() )           
           self.resizeevent= self.resizeBottom
         else:
           self.setMinimumSize(0, 0)       
           self.setMaximumSize(self.maximumHeight(),self.maximumHeight())
           self.setGeometry(self.x(), self.y(), self.height(), 60) # Swap width & height
           self.setMinimumSize(300, 60)       
           self.setMaximumSize(self.maximumHeight(),60)                      
           self.resizeevent= self.resizeRight
  
         self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
                
        if not self.transparent_action.isChecked():
          painter.fillRect(self.rect(), QColor(self.colors_bg[self.current_color]))

        unit_size = self.convert2pixels(1) #get unit_size in px
        
        #Settings for ticks
        painter.setFont(QFont("Arial", 12))
        pen_thk = QPen(QColor(self.colors_markers[self.current_color]),2) #thicker
        pen_thn = QPen(QColor(self.colors_markers[self.current_color]),1) #thinner
        painter.setPen(pen_thk)
        
        height_minor = 8
        height_major = 15
        
        if self.is_vertical:
          painter.drawText(20,20, self.unitshorts[self.unit])   #Write unit
          painter.save()  
          painter.rotate(-90) #rotate counter-clockwise

          for i in np.arange(0, self.height(), unit_size):

            if i>0:  # Draw major ticks
              painter.setPen(pen_thk)
              painter.drawLine(QPointF(-i, 0), QPointF(-i, height_major))
              painter.drawLine(QPointF(-i, 60-height_major), QPointF(-i, 60))
              text = str("%g" % (i / unit_size)) if self.unit != "Pixels" else str(i)            
              painter.drawText(QRectF(-i-20, 20, 40, 20), Qt.AlignCenter, text) # Write number
            
            #Minor marks 
            for j in np.arange(i + unit_size/10.0, i + unit_size, unit_size/10.0):
               painter.setPen(pen_thn)
               painter.drawLine(QPointF(-j, 0), QPointF(-j, height_minor))
               painter.drawLine(QPointF(-j, 60-height_minor), QPointF(-j, 60))

            #Mid-ticks
            painter.setPen(pen_thk)
            painter.drawLine(QPointF( -i-0.5*unit_size, 0), QPointF( -i-0.5*unit_size, height_minor+3) )
            painter.drawLine(QPointF( -i-0.5*unit_size, 60-height_minor-3), QPointF( -i-0.5*unit_size, 60) )
      
          painter.restore()
          
        else:
          painter.drawText(5,35, self.unitshorts[self.unit])  #Write unit
        
          for i in np.arange(0, self.width(), unit_size): 
           
            if i>0: # Draw major ticks
              painter.setPen(pen_thk)
              painter.drawLine(QPointF(i, 0), QPointF(i, 15))
              painter.drawLine(QPointF(i, 45), QPointF(i, 60))
              text = str("%g" % (i / unit_size)) if self.unit != "Pixels" else str(i)            
              painter.drawText(QRectF(i-20, 20, 40, 20), Qt.AlignCenter, text) # Write number
            
            #Minor marks 
            for j in np.arange(i + unit_size/10.0, i + unit_size, unit_size/10.0):
               painter.setPen(pen_thn)
               painter.drawLine(QPointF(j, 0), QPointF(j, height_minor))
               painter.drawLine(QPointF(j, 60-height_minor), QPointF(j, 60))

            #Mid-ticks
            painter.setPen(pen_thk)
            painter.drawLine(QPointF( i+0.5*unit_size, 0), QPointF( i+0.5*unit_size, height_minor+3) )
            painter.drawLine(QPointF( i+0.5*unit_size, 60-height_minor-3), QPointF( i+0.5*unit_size, 60) )

        
        painter.end()
      

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            if self.is_vertical:
               relative_mouse_position = self.frameGeometry().height() - self._drag_position.y()  
            else: 
               relative_mouse_position = self.frameGeometry().width() - self._drag_position.x()
            if relative_mouse_position  < self.margin :
                self._resize_active = True
                self._resizePos = event.globalPos()                
            else:
                self._drag_active = True
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.move(event.globalPos() - self._drag_position)
        elif self._resize_active:
            delta = event.globalPos() - self._resizePos
            self._resizePos = event.globalPos()
            self.resizeevent(delta)  
            event.accept()
        else:
          if (self.frameGeometry().width() - event.x()  < 8) and not(self.is_vertical) :
            self.setCursor(Qt.SizeHorCursor) # Change cursor around the right edge
          elif (self.frameGeometry().height() - event.y()  < 8) and (self.is_vertical) :
            self.setCursor(Qt.SizeVerCursor) # Change cursor around the bottom edge            
          else:
            self.setCursor(Qt.ArrowCursor)  # Default cursor
        

    def mouseReleaseEvent(self, event):
        self._drag_active    = False
        self._resize_active  = False
 
    def resizeRight(self, delta):
        new_width = self.frameGeometry().width() + delta.x(); new_height= self.frameGeometry().height()
        self.resize(new_width, new_height)
        self.update()        
    
    def resizeBottom(self, delta):
        new_width = self.frameGeometry().width(); new_height= self.frameGeometry().height()+delta.y()
        self.resize(new_width, new_height)
        self.update()        


    def nextunit(self):
        """Switch to the next unit"""
        actions = self.unit_group.actions()
        for i, action in enumerate(actions):
           if action.isChecked():
#              print("Label:", action.text(), "Checked:", action.isChecked())
              break                #Find the index of the current unit

        actions[ (i+1)%len(actions) ].setChecked(True)  #Next unit is checked 
#        actions[ (i  )%len(actions) ].setChecked(False) #The current unit is unchecked       
        actions[ (i+1)%len(actions) ].trigger()         #Next unit is triggered



    def change_unit(self, unit_var):
        """Change the unit and update the ruler."""
        self.unit = unit_var
        self.update()


    def convert2pixels(self, value):
        """Convert cm or inches to pixels using detected DPI."""
        screen = self.window().windowHandle().screen()
        dpi = screen.logicalDotsPerInch()
#        dpi = screen.physicalDotsPerInch() #alternative
        #debug
#        print("Current screen:", screen.name())
#        print("DPI:", screen.logicalDotsPerInch())
        
        if self.unit == "Centimeters":
            return value * (dpi / 2.54)  # 1 cm = 2.54 inches
        elif self.unit == "Inches":
            return value * dpi  # 1 inch = DPI pixels
        else:
            return 100 * value  # Pixels stay the same but step of the marker is 100


    def change_theme(self):
        keys = list(self.colors_bg.keys())
        for i,clr in enumerate(keys): 
          if self.current_color==clr:
            break           
        self.current_color=keys[ (i+1)%len(keys) ]    
        self.update()

          
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScreenRuler()
    window.show()
    sys.exit(app.exec_())

