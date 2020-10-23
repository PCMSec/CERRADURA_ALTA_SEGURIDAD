from tkinter import *

def show_data():
    print( 'My First and Last Name are %s' % (contador_usuario.get()) )

def generar_ventana():
	ventana = Tk()

	Label(ventana, text='Contador del usuario').grid(row=0)

	contador_usuario = Entry(ventana)

	contador_usuario.grid(row=0, column=1)

	Button(ventana, text='Exit', command=ventana.quit).grid(row=3, column=0, sticky=W, pady=4)
	Button(ventana, text='Show', command=show_data).grid(row=3, column=1, sticky=W, pady=4)

	mainloop()