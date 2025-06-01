# Créé par Marc Tissier1, le 14/02/2025 en Python 3.7
#Saisie du pseudo pour enregistrer le score dans la base de donnees
import sqlite3
from tkinter import *

largeur_ecran=1200
hauteur_ecran=500
#Enregistrement des donnees dans une base de donnees

def sendscore(val):
    global score
    score = val

def show_score_window():
    global score
    if score > 0:
        fen = Tk()
        fen.title('Enregistrer les scores.')
        fen.geometry('500x120')
        L = Label(fen, text="Entrez votre pseudo:", width=35, fg="blue", bg="yellow")
        L.place(x=20, y=20)
        E = Entry(fen)
        E.place(x=280, y=20)
        E.focus()

        def quitter():
            fen.quit()

        def enregistrer():
            texteSurnom = E.get()
            nouvelle_personne = (texteSurnom, score)
            connexion = sqlite3.connect('scores.db')
            curseur = connexion.cursor()
            curseur.execute("CREATE TABLE IF NOT EXISTS PERSONNE(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,surnom TEXT, score INT)")
            curseur.execute("INSERT INTO PERSONNE(surnom,score) VALUES(?,?)", nouvelle_personne)
            connexion.commit()
            curseur.close()
            connexion.close()
            fen.quit()
            # Store texteSurnom for later use in the next window
            fen.texteSurnom = texteSurnom

        def quitter():
            fen.quit()

        B1 = Button(fen, text="Valider", fg="green", bg="white", command=enregistrer)
        B1.place(x=20, y=70)
        fen.protocol("WM_DELETE_WINDOW", quitter)
        fen.mainloop()
        # Retrieve texteSurnom after fen is closed
        texteSurnom = getattr(fen, 'texteSurnom', '')

        fen.destroy()

        # Affichage des meilleurs scores
        fen1 = Tk()
        fen1.title('MEILLEURS SCORES.')
        fen1.geometry('450x300')
        L = Label(fen1, text="Entrez vous dans la légende ?", width=25, fg="blue", bg="yellow")
        L.place(x=20, y=20)
        L1 = Label(fen1, text="Surnom", width=10, fg="blue", bg="yellow")
        L1.place(x=210, y=20)
        L2 = Label(fen1, text="temps", width=8, fg="blue", bg="yellow")
        L2.place(x=300, y=20)
        L1.config(text=texteSurnom)
        L2.config(text=score)
        L3 = Label(fen1, text="TOP Scores", width=22, fg="blue", bg="yellow")
        L3.place(x=20, y=50)
        L4 = Label(fen1, text="Vos meilleurs scores.", width=22, fg="blue", bg="yellow")
        L4.place(x=250, y=50)
        # Affichage des Top scores
        S_labels = []
        N_labels = []
        T_labels = []
        for i in range(5):
            S = Label(fen1, text=str(i + 1), width=3, fg="yellow", bg="blue")
            S.place(x=20, y=80 + i * 30)
            N = Label(fen1, text="", width=12, fg="yellow", bg="blue")
            N.place(x=50, y=80 + i * 30)
            T = Label(fen1, text="", width=4, fg="yellow", bg="blue")
            T.place(x=143, y=80 + i * 30)
            S_labels.append(S)
            N_labels.append(N)
            T_labels.append(T)
        # Affichage des meilleurs scores du joueur
        S11 = Label(fen1, text="1", width=3, fg="yellow", bg="blue")
        S11.place(x=250, y=80)
        S12 = Label(fen1, text="2", width=3, fg="yellow", bg="blue")
        S12.place(x=250, y=110)

        N11 = Label(fen1, text="", width=12, fg="yellow", bg="blue")
        N11.place(x=280, y=80)
        N12 = Label(fen1, text="", width=12, fg="yellow", bg="blue")
        N12.place(x=280, y=110)
        T11 = Label(fen1, text="", width=4, fg="yellow", bg="blue")
        T11.place(x=373, y=80)
        T12 = Label(fen1, text="", width=4, fg="yellow", bg="blue")
        T12.place(x=373, y=110)
        # Recherche des meilleurs scores
        connexion = sqlite3.connect('scores.db')
        curseur = connexion.cursor()
        curseur.execute('SELECT surnom,score FROM PERSONNE ORDER BY score DESC LIMIT 5')
        liste = curseur.fetchall()
        curseur.close()
        connexion.close()

        for i, entry in enumerate(liste):
            N_labels[i].config(text=entry[0])
            T_labels[i].config(text=entry[1])
        # Recherche des meilleurs scores du joueur
        connexion = sqlite3.connect('scores.db')
        curseur = connexion.cursor()
        recherche = (texteSurnom, 0)
        curseur.execute('SELECT surnom,score FROM PERSONNE WHERE surnom= ? AND score> ? ORDER BY score DESC LIMIT 2', recherche)
        connexion.commit()
        liste = curseur.fetchall()
        n = len(liste)
        if n > 0:
            N11.config(text=liste[0][0])
            T11.config(text=liste[0][1])
        if n > 1:
            N12.config(text=liste[1][0])
            T12.config(text=liste[1][1])
        curseur.close()
        connexion.close()
        B2 = Button(fen1, text="quitter", fg="green", bg="white", command=fen1.quit)
        B2.place(x=180, y=260)
        fen1.mainloop()

        fen1.destroy()
