#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 18:47:43 2025

@author: sachinkalahasti
"""
import sqlite3
import pandas as pd
import streamlit as stl
import matplotlib.pyplot as plt


def get_db_connection():
    conn = sqlite3.connect('task_organizer.db')
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.executescript('''
                   CREATE TABLE IF NOT EXISTS tasks(
                       task_id INTEGER PRIMARY KEY,
                       task_title TEXT NOT NULL,
                       task_description TEXT NOT NULL,
                       task_status TEXT NOT NULL CHECK(task_status IN ('pending', 'completed')) DEFAULT 'pending',
                       task_time TIME NOT NULL DEFAULT '00:00');
                   ''')
    conn.commit()
    conn.close()
    
def add_task(task_title, task_description, task_time):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    task_time_str = task_time.strftime('%I:%M %p')
    
    cursor.execute('''
                   INSERT INTO tasks (task_title, task_description, task_time)
                   VALUES (?, ?, ?);
                   ''', (task_title, task_description, task_time_str))
    conn.commit()
    conn.close()
    
def view_alltasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   SELECT * FROM tasks
                   ORDER BY task_time;
                   ''')
    tasks = cursor.fetchall()
    conn.commit()
    conn.close()

    return tasks

def update_task(task_id, task_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   UPDATE tasks
                   SET task_status = ?
                   WHERE task_id = ?;
                   ''', (task_status, task_id))
    conn.commit()
    conn.close()
    
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   DELETE FROM tasks
                   WHERE task_id = ?;
                   ''', (task_id))
    conn.commit()
    conn.close()

def view_status_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
                   SELECT task_status, COUNT(*) from tasks
                   GROUP BY task_status;
                   ''')
    status = dict(cursor.fetchall())
    conn.commit()
    conn.close()
    
    return status


def app():
    create_table()
    stl.title("Task Manager")
    menu = ["Add Task", "View All Tasks", "Update Task Status", "Delete Task", "Productivity Graph"]
    choice = stl.sidebar.selectbox("Menu", menu)
    if choice == "Add Task":
        stl.header("Add Task")
        task_title = stl.text_input('Task')
        task_description = stl.text_input('Description')
        task_time = stl.time_input("Due Time")
        formatted_time = task_time.strftime('%I:%M %p')
        stl.write(f"Selected Due Time: {formatted_time}")
        
        if stl.button('Add'):
            if task_title and task_description and task_time:
                add_task(task_title, task_description, task_time)
                stl.info("New Task Has Been Added")
            else:
                stl.error("Please Fill In All Required Fields")
                
    elif choice == "View All Tasks":
        stl.header("All Tasks")
        tasks = view_alltasks()
        if len(tasks) == 0:
            stl.info("No Assigned Tasks")
        else:
            columns = ['ID', 'Task', 'Description', 'Status', 'Time']

            # Create a DataFrame
            tasks = pd.DataFrame(tasks, columns=columns)
            
            # Display the table in Streamlit
            stl.write(tasks)
            
    elif choice == "Update Task Status":
        stl.header("Update Task Status")
                          
        task_id = stl.text_input('Task ID')
        task_status = stl.text_input("Task Status")
        if stl.button('Update'):
            if task_id and task_status:
                update_task(task_id, task_status)
                stl.info("Task Status Has Been Update")
            else:
                
                stl.error("Please Fill In All Required Fields")
    
    elif choice == "Delete Task":
        stl.header("Delete Task")
        task_id = stl.text_input('Task ID')
        if stl.button('Delete'):
            if (task_id):
                delete_task(task_id)
                stl.info("Task Has Been Deleted")
            else:
                stl.error("Please Fill In All Fields")
   
    elif choice == "Productivity Graph":
        stl.header("Productivity Graph")
        status = view_status_count()
        
        fig, ax = plt.subplots()
        ax.bar(status.keys(), status.values())
        ax.set_xlabel('Status')
        ax.set_ylabel('# of Tasks')
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        stl.pyplot(fig)
    
if __name__ == '__main__':
    app()