
from datetime import datetime
import sys, json
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QListWidget,
)
from PyQt5.QtCore import Qt

#MEMORIA PRINCIPAL
inventario = {} #inventario de articulos
inventario['inventario']=[] #codificacion json
listacuenta = [] #cuenta a pagar, vector de listas de tres valores (nombre, precio, cantidad)
listaStock = {'Nombre': None, 'Stock':None} #stock nuevo: (nombre, cantidad)
precioTotal= 0
#FUNCIONES VARIAS archivos y memoria principal
def leerInventario(): #lee archivo json 
    with open('inventario.json') as file:
        data = json.load(file)
        for articulo in data['inventario']: #carga en memoria el json
            inventario['inventario'].append({'Nombre':articulo['Nombre'],'Precio':articulo['Precio'], 'Stock':articulo['Stock']})
    file.close()

def escribirInventario(): #escribe archivo json
    with open('inventario.json', 'w') as file: 
        json.dump(inventario, file, indent=3) #escribe el inventario codificado
    file.close()

def escribirLog(precioTotal): #escribe fichero de logs de pagos
    with open('log.txt', 'a') as file:
        file.write("\n-----------------------------\n")
        file.write(datetime.today().strftime('%Y-%m-%d %H:%M'))
        for item in listacuenta:
            file.write(str("\n" + item[2] + " -> " + item[0]))
        file.write("\nPagado: " + str(precioTotal) + " €")
    file.close()

def escribirStock(): #escribe en memoria principal para cambiar el stock
    nombre = listaStock['Nombre'].split(' (')
    for articulo in inventario['inventario']: #recorre memoria
        if articulo['Nombre'] == nombre[0]: #comprueba registro
            articulo['Stock'] += listaStock['Stock'] #añade el stock
        print(articulo['Nombre'], nombre)

def recalculoStock():#calcula nuevo stock despues de retirada
    for articulo in inventario['inventario']:#recorre inventario
        for item in listacuenta:#recorre cuenta
            if(item[0]==articulo["Nombre"]): #comprueba 
                articulo["Stock"]-=int(item[2])  #cambio de stock

def calcularCuenta(total): #calcula cuenta a pagar
    for articulo in listacuenta: #recorre cuenta
        precio = articulo[1].split(" €") #recoge el precio
        total = total + (float(precio[0]) * int(articulo[2])) #precio*cantidad
    return total

#ventana stock
class Stockwindow(QWidget): 
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Añadir stock")
        layout = QGridLayout()
        self.listaConsumiciones = QListWidget() #lista de consumiciones 
        for i in range(len(inventario['inventario'])):
            self.listaConsumiciones.insertItem(i, inventario['inventario'][i]['Nombre'] + " (" + str(inventario['inventario'][i]['Stock']) + " uds)") #inicia lista
        layout.addWidget(self.listaConsumiciones, 1, 0)
        self.listaConsumiciones.clicked.connect(self.numerico)
        self.selInt = QSpinBox(self)
        self.selInt.setMinimum(0)
        self.selInt.setMaximum(99)
        self.selInt.setValue(0)
        self.selInt.valueChanged.connect(self.numerico)
        layout.addWidget(self.selInt, 0, 0)
        self.botonAnhadir = QPushButton("Añadir stock") #boton anhadir
        self.botonAnhadir.setEnabled(False)#boton desactivado
        self.botonAnhadir.clicked.connect(self.anhadir)
        layout.addWidget(self.botonAnhadir, 2, 0)
        self.botonRechazar = QPushButton("Atrás") #boton anhadir
        self.botonRechazar.clicked.connect(self.rechazar)
        layout.addWidget(self.botonRechazar, 2, 1)
        self.setLayout(layout)#despliegue
    
    def closeEvent(self, event):#control de ventana
        self.rechazar()

    def numerico(self): #activa boton añadir con seleccion
        if self.selInt.value()>0 and self.listaConsumiciones.currentRow()!=-1:
            self.botonAnhadir.setEnabled(True)
        else:
            self.botonAnhadir.setEnabled(False)
        if self.listaConsumiciones.currentItem()!=None:
            listaStock['Nombre']= self.listaConsumiciones.currentItem().text()
            listaStock['Stock']= self.selInt.value()

    def anhadir(self):
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        self.w = PopwindowStock() #crea ventana de confirmacion
        self.w.show()#despliegue
    
    def rechazar(self):
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        self.w = Window() #crea ventana de confirmacion
        self.w.show()#despliegue

#ventana de confirmacion de stock
class PopwindowStock(QWidget): 
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Confirmar cuenta")
        self.setFixedWidth(500)
        self.setFixedHeight(100)
        layout = QGridLayout()
        self.labelCuenta1 = QLabel("Se añadirán " + str(listaStock['Stock']) + " uds de")
        self.labelCuenta1.setAlignment(Qt.AlignRight)
        layout.addWidget(self.labelCuenta1, 0, 0)
        self.labelCuenta2 = QLabel(str(listaStock['Nombre']) + " al stock")
        self.labelCuenta2.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.labelCuenta2, 0, 1)
        self.butonConfirmar = QPushButton("Confirmar")
        self.butonConfirmar.clicked.connect(self.confirmar)
        layout.addWidget(self.butonConfirmar, 1, 0)#boton rechazar
        self.butonRechazar = QPushButton("Rechazar")
        self.butonRechazar.clicked.connect(self.rechazar)
        layout.addWidget(self.butonRechazar, 1, 1)
        self.setLayout(layout)#despliegue

    def closeEvent(self, event):#control de ventana
        self.rechazar()

    def confirmar(self):#confirma pago
        escribirStock()
        escribirInventario()
        listacuenta.clear() #limpia cuenta
        self.close() #cierra venta
        self.destroy() #destruye objeto
        self.w = Stockwindow() #crea ventana de confirmacion
        self.w.show() #nueva ventana
    
    def rechazar(self):
        listacuenta.clear() #limpia cuenta
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        self.w = Stockwindow() #crea ventana de confirmacion
        self.w.show() #nueva ventana

#ventana principal
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software autogestor")
        self.setFixedWidth(850)
        self.setFixedHeight(380)
        self.row=0
        layout = QGridLayout()
        self.listaConsumiciones = QListWidget() #lista de consumiciones
        for i in range(len(inventario['inventario'])):
            self.listaConsumiciones.insertItem(i, inventario['inventario'][i]['Nombre']) #inicia lista
        layout.addWidget(self.listaConsumiciones, 1, 0) #lista ui
        self.tablaCuenta = QTableWidget(1, 3)#tabla cuenta
        self.tablaCuenta.setHorizontalHeaderLabels(['Nombre', 'Precio', 'Cantidad'])
        self.tablaCuenta.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tablaCuenta, 1, 2)
        self.botonStock = QPushButton("Stock") #boton stock
        self.botonStock.clicked.connect(self.stock)
        layout.addWidget(self.botonStock, 2, 0)
        self.botonCuenta = QPushButton("\t->\t") #boton
        self.botonCuenta.clicked.connect(self.anhadir)
        layout.addWidget(self.botonCuenta, 1, 1)
        self.botonBorrar = QPushButton("Borrar") #boton2
        self.botonBorrar.setEnabled(False)#boton borrar
        self.botonBorrar.clicked.connect(self.borrar)
        layout.addWidget(self.botonBorrar, 2, 2)
        self.botonPagar = QPushButton("Pagar") #boton3
        self.botonPagar.setEnabled(False)#boton pago
        self.botonPagar.clicked.connect(self.retirar)
        layout.addWidget(self.botonPagar, 1, 3)
        self.setLayout(layout)#despliegue
        
    def closeEvent(self, event):#control de ventana
        self.close()
        self.destroy()
        self.listaConsumiciones.clear()
        self.listaConsumiciones.destroy()
        
    def anhadir(self): #añade un elemento a la cuenta
        item=self.listaConsumiciones.currentItem().text() #item seleccionado
        for i in inventario['inventario']: #memoria principal
            if i['Nombre'] == item:
                nombre = i['Nombre']
                precio = str(i['Precio']) + " €"
                cantidad = str(1)
        #Clear current selection.
        self.tablaCuenta.setCurrentItem(None)
        matching_items = self.tablaCuenta.findItems(item, Qt.MatchContains)
        if matching_items: #si ya existe
            indice = self.tablaCuenta.indexFromItem(matching_items[0]) #busca indice del elemento
            cantidad = str(int(self.tablaCuenta.model().index(indice.row(), 2).data()) + 1) #suma 1 a la cantidad de la fila
            self.tablaCuenta.setItem(indice.row(), 0, QTableWidgetItem(nombre))
            self.tablaCuenta.setItem(indice.row(), 1, QTableWidgetItem(precio))
            self.tablaCuenta.setItem(indice.row(), 2, QTableWidgetItem(cantidad))
        else: #si no existe la fila es nueva
            if(self.row>0): 
                self.tablaCuenta.insertRow(self.row)
            self.tablaCuenta.setItem(self.row, 0, QTableWidgetItem(nombre))
            self.tablaCuenta.setItem(self.row, 1, QTableWidgetItem(precio))
            self.tablaCuenta.setItem(self.row, 2, QTableWidgetItem(cantidad))
            self.row += 1 #cuenta el numero de filas
        self.botonPagar.setEnabled(True)#activa boton de pago
        self.botonBorrar.setEnabled(True)#boton borrar

    def stock(self):
        self.w = Stockwindow() #crea ventana de confirmacion
        self.w.show()#despliegue
        self.borrar()#borra datos
        self.close()
        self.destroy()

    def borrarTabla(self):
        if self.row>1: #si hay filas las borra
            for i in range(0,self.tablaCuenta.rowCount()): #recorre tabla
                self.tablaCuenta.removeRow(i)#borra filas
        self.tablaCuenta.clearContents() #borra contenido

    def borrar(self): #limpia la tabla
        self.borrarTabla()
        listacuenta.clear#borra cuenta
        self.row=0#borra cuenta de filas
        self.botonPagar.setEnabled(False)#desactiva boton pagar
        self.botonBorrar.setEnabled(False)#boton borrar
        
    def retirar(self): #pagar la cuenta
        for i in range(0,self.tablaCuenta.rowCount()):
            auxlist=[]
            for j in range(0, 3):
                item = self.tablaCuenta.item(i, j).text()
                auxlist.append(item)
            listacuenta.append(auxlist)
        self.borrarTabla()#borra tabla
        self.close()#cierra ventana
        self.destroy()#destruye objeto
        self.w = Popwindow() #crea ventana de confirmacion
        self.w.show()#despliegue

#ventana de confirmacion de cuenta
class Popwindow(QWidget): 
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Confirmar cuenta")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        layout = QGridLayout()
        self.labelTotal = QLabel("Total =") #muestra el total de la cuenta
        self.labelTotal.setAlignment(Qt.AlignRight)
        layout.addWidget(self.labelTotal, 0, 0)
        self.labelCuenta = QLabel(str(calcularCuenta(precioTotal))+ " €")
        self.labelCuenta.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.labelCuenta, 0, 1)#boton confirmar
        self.butonConfirmar = QPushButton("Confirmar")
        self.butonConfirmar.clicked.connect(self.confirmar)
        layout.addWidget(self.butonConfirmar, 3, 0)#boton rechazar
        self.butonRechazar = QPushButton("Rechazar")
        self.butonRechazar.clicked.connect(self.rechazar)
        layout.addWidget(self.butonRechazar, 3, 1)
        self.setLayout(layout)#despliegue

    def closeEvent(self, event):#control de ventana
        self.rechazar()
        

    def confirmar(self):#confirma pago
        recalculoStock() 
        escribirInventario()
        escribirLog(calcularCuenta(precioTotal))
        self.close() #cierra venta
        self.destroy() #destruye objeto
        self.w = confPopwindow() #crea ventana de confirmacion
        self.w.show() #nueva ventana
    
    def rechazar(self):
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        self.w = rechPopwindow() #crea ventana de rechazo
        self.w.show() #nueva ventana

class confPopwindow(QWidget): 
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Confirmar cuenta")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        layout = QGridLayout()
        self.labelTitulo = QLabel("PAGADO")
        self.labelTitulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.labelTitulo, 0, 0)
        i=1
        for articulo in listacuenta:
            self.labelTotal = QLabel(articulo[0]) #muestra el total de la cuenta
            self.labelTotal.deleteLater()
            self.labelTotal.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.labelTotal, i, 0)
            i+=1
        self.butonAceptar = QPushButton("Aceptar")
        self.butonAceptar.clicked.connect(self.aceptar)
        layout.addWidget(self.butonAceptar, i+1, 0)
        self.setLayout(layout)#despliegue

    def closeEvent(self, event):#control de ventana
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        self.w = Window()
        self.w.show()

    def aceptar(self):
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        listacuenta.clear() #limpia cuenta
        self.w = Window() #crea ventana principal
        self.w.show() #nueva ventana

class rechPopwindow(QWidget): 
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Confirmar cuenta")
        self.setFixedWidth(300)
        self.setFixedHeight(100)
        layout = QGridLayout()
        self.labelTotal = QLabel("Operación cancelada") #muestra cancelacion
        self.labelTotal.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.labelTotal, 0, 0)
        self.butonAceptar = QPushButton("Aceptar")
        self.butonAceptar.clicked.connect(self.aceptar)
        layout.addWidget(self.butonAceptar, 1, 0)
        self.setLayout(layout)#despliegue
    
    def closeEvent(self, event):#control de ventana
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        self.w = Window()
        self.w.show()

    def aceptar(self):
        self.close() #cierra ventana
        self.destroy() #destruye objeto
        listacuenta.clear() #limpia cuenta
        self.w = Window() #crea ventana principal
        self.w.show() #nueva ventana

#MAIN
if __name__ == "__main__":
    '''for p in psutil.process_iter():
        if(p.name()=='python3'):
            pid=p.pid
    print(pid, p.name())'''
    leerInventario()#lectura de datos del inventario
    app = QApplication(sys.argv)#aplicacion
    window = Window()#objeto ventana
    window.show()#despliegue de ventana principal
    ##salir del programa
    sys.exit(app.exec_())
    