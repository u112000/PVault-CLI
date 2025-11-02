#===========================================================
# Script Name: PVault.py +
# Author: u112000
# Created: 2025-11-02
# Last Updated: 2025-11-02
# Version: 1.0.0
# Description:
#     The program was created by constant curiosity and persistence to complete old forgotten projects.
#     It serves as a POC of what can/could be created with just as little as an "if...else:" statement.
#     for the curious minds..
#===========================================================

#! python3

import os, typer
from rich import print
from rich.panel import Panel
import sqlite3, secrets
from encryption_management import CryptographyLogic

app = typer.Typer(add_completion=False)
encrytion_connection = CryptographyLogic()

def database_management(operationType='CLOSE'):
    global connection, cursor
    if operationType == 'OPEN':
        try:
            connection = sqlite3.connect('vault_database.sqlite3')
            cursor = connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS vault_db (
                       url TEXT NOT NULL,
                       password TEXT NOT NULL)''')
            data = cursor.execute('SELECT password FROM vault_db').fetchall()
            if len(data) != 0:
                for each_password_tuple in data:
                    cursor.execute('UPDATE vault_db SET password = ? WHERE password = ?', (encrytion_connection.decryption(each_password_tuple[0]), each_password_tuple[0]))
        except:
            printer("A critical issue was detected. Database session terminated for safety.", title="DATABASE ERROR")
            connection.rollback()
            database_management()
    else:
        data = cursor.execute('SELECT password FROM vault_db').fetchall()
        if len(data) != 0:
            for each_password_tuple in data:
                cursor.execute('UPDATE vault_db SET password = ? WHERE password = ?', (encrytion_connection.encryption(each_password_tuple[0]), each_password_tuple[0]))
        connection.commit()
        cursor.close()
        connection.close()

def printer(data, title="WARNING", colour="red"):
    if colour == 'green':
        print(Panel.fit(data,
            title=f"[bold green]{title}[/bold green]",
            border_style="bold green"))
    elif colour == 'red':
        print(Panel.fit(data,
            title=f"[bold red]⚠ {title}[/bold red]",
            border_style="bold red"))

@app.command()
def Update_login_password(url: str = typer.Option(help="Url"),
                          newpassword: str = typer.Option(help="New password to adjust too")):
    database_management('OPEN')
    checker = cursor.execute('SELECT * FROM vault_db WHERE url = ?', (url,)).fetchall()
    if checker != []:
        cursor.execute('''UPDATE vault_db SET password = ? WHERE url = ?''', (newpassword, url))
        database_management()
        printer(f"The password for [bold yellow]{url}[/bold yellow] has been updated.\n\nNew Password: [bold yellow]{newpassword}[/bold yellow]", title="UPDATE SUCCESSFUL", colour="green")
    else:
        database_management()
        printer(f"The specified URL [bold yellow]{url}[/bold yellow] does not exist in the database.", title="ERROR")

@app.command()
def Generate_Newkeys():
    print(encrytion_connection.Generate_DBkeys())

@app.command()
def Register_credentials(url: str = typer.Option(help="Url"),
             passwd: str = typer.Option(help="Password of the Url")):
    database_management('OPEN')
    if cursor.execute('SELECT * FROM vault_db WHERE url = ?',(url,)).fetchall() == []:
        cursor.execute('INSERT INTO vault_db (url, password) VALUES (?, ?)', (url, passwd))
        database_management()
        printer(f"Credentials have been saved successfully.\n[dim]URL:[/dim] [bold yellow]{url}[/bold yellow]\n[dim]Password:[/dim] [bold yellow]{passwd}[/bold yellow]", "ENTRY ADDED", "green")
    else:
        database_management()
        printer(f"The URL [bold yellow]{url}[/bold yellow] already exists in the database.", title="DUPLICATE ENTRY")

@app.command()
def List_credentials():
    database_management('OPEN')
    data = cursor.execute('SELECT url FROM vault_db').fetchall()
    if data != []:
        print(f'| Index- URLs IN DATABASE::\n--------------------------')
        counter_ = 0
        for i in data:
            counter_ += 1
            print(f'| < {counter_} >  [bold yellow]{i[0]}[/bold yellow]')
        database_management()
    else:
        printer(f"No credentials found in the database. Add entries to view stored data.")
        database_management()

@app.command()
def View_credentials(url: str = typer.Option(help="Url to retrieve")):
    database_management('OPEN')
    data = cursor.execute('SELECT password FROM vault_db WHERE url = ?', (url,)).fetchall()
    if data != []:
        raw_passwd = data[0][0]
        printer(f"[bold cyan]URL:[/bold cyan] [bold yellow]{url}[/bold yellow]\n[bold cyan]Password:[/bold cyan] [bold yellow]{raw_passwd}[/bold yellow]", "NOTICE", "green")
    else:
        printer(f"No record found for [bold yellow]{url}[/bold yellow].", "LOOKUP FAILED")
        database_management()

if __name__ == "__main__":
    app()
