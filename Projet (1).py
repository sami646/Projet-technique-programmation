#!/usr/bin/env python
# coding: utf-8

# # Fonctions collecte données musées

# In[ ]:


from bs4 import BeautifulSoup
import urllib3
import re
import time
from collections import defaultdict
import numpy as np
import tqdm
import requests


# In[ ]:


def clean_list(urlpage, raw_museum_list):
  # nettoie la liste de musées pour ne garder qu'un dictionnaire avec comme clé le nom du musée et comme valeur le lien url du musée
  cleaned_links = {}
  for link in raw_museum_list:
    name = re.findall(r'<span>(.*?)</span>', str(link))[0]
    link = urlpage + re.findall('href="(.*?)" style', str(link))[0]
    cleaned_links.update({name:link})
  return cleaned_links

def get_museums_links(urlpage):
  # on fait une requête GET pour obtenir le contenu HTML de la page
  page = requests.get(urlpage + "/decouvrir")
  # on utilise BeautifulSoup pour analyser le HTML
  soup = BeautifulSoup(page.content, 'html.parser')
  # on cherche toutes les infos dans 'section'
  liste = soup.find('section', {'id': 'rubric', 'class': 'margin-bottom'})
  liste = str(liste).split("aria-label=")[1:]
  return clean_list(urlpage, liste)


# In[ ]:


def get_info(museum_link, info_type):
  # retourne l'info demandée sur le musée
  page = requests.get(museum_link)
  soup = BeautifulSoup(page.content, 'html.parser')
  if info_type == "prix ticket":
    price = re.findall(r'<p>(.*?)</p>', page.text)[0]
    return re.sub(r'&nbsp;', '  ', re.findall(r'<strong>(.*?)</strong>', price)[0])
  elif info_type in ("jours ouverture", "heures ouverture"):
    horaire = soup.find('div', class_=re.compile(r'des+')).text.split('\n')
    if info_type == "jours ouverture":
      return horaire[0]
    else:
      return horaire[1]
  elif info_type == "description":
    return re.findall(r'<p>(.*?)</p>', page.text)[1]

def print_info(museum_link,info_type, visitor_answer):
  # affiche l'info sur le musée si le visiteur a répondu oui à la question
  if visitor_answer == "oui":
    info = get_info(museum_link, info_type)
    print(info)
    print('-------------------------------------------------------------------')


# In[ ]:


def museum_assistant(urlpage):
  # Fonction principale
  museum_links = get_museums_links(urlpage)
  while True:
    musee = input("Quel musée voulez-vous voir parmi les suivants? \n \n1)Musée Archéologique \n2)Musée des Arts Décoratifs \n3)Musée d’Art moderne et contemporain \n4)Musée Historique \n5)Musée de l’Œuvre Notre-Dame \n6)Aubette 1928 \n7)Musée Zoologique \n\n   ")

    if musee in museum_links:
      print('-------------------------------------------------------------------')
      reponse_desc = input("Voulez-vous voir la description du musée? (oui/non) \n\n  ")
      print_info(museum_links[musee], "description", reponse_desc)

      reponse_ticket = input("Voulez-vous voir le prix du ticket du musée? (oui/non) \n\n  ")
      print_info(museum_links[musee], "prix ticket", reponse_ticket)

      reponse_jours = input("Voulez-vous savoir quels sont les jours d'ouverture du musée? (oui/non) \n\n  ")
      print_info(museum_links[musee], "jours ouverture", reponse_jours)

      reponse_heures = input("Voulez-vous savoir quels sont les horaires d'ouverture du musée? (oui/non) \n\n  ")
      print_info(museum_links[musee], "heures ouverture", reponse_heures)
      
      final_question = input("Voulez vous afficher l'information sur un autre musée? (oui/non) \n\n")
      if final_question == 'non':
        break
    else:
        print("Musée non trouvé. Veuillez réessayer.")
        print('-------------------------------------------------------------------')


# In[ ]:


#to call the code above :


# In[ ]:


museum_assistant("https://www.musees.strasbourg.eu")


# # Fonctions réservation de groupe

# In[ ]:


import selenium
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
import time


# In[ ]:


def open_webpage(url):
    web = webdriver.Chrome()
    web.get(url)
    return web


# In[ ]:


def select_museum(web, musees_visiter):
    musee_choisis = '//*[@id="var_musee"]/div[2]/label[{}]/span'.format(musees_visiter)
    element = web.find_element(By.XPATH, musee_choisis)
    element.click()

def select_group_type(web, type_de_public):
    type_public_choisi = '//*[@id="var_groupes"]/div[2]/label[{}]/span'                            .format(type_de_public)
    groupe = web.find_element(By.XPATH, type_public_choisi)
    groupe.click()

def select_number_of_people(web, nombre_de_personnes):
    nombre = web.find_element(By.XPATH, '/html/body/main/div[4]/div/div/div/div/div/div/div[3]/form/div[6]/div[2]/input')
    web.execute_script("arguments[0].value = arguments[1];", nombre, nombre_de_personnes)

def select_type_of_person(web, person_type):
    selection_type_personne = web.find_element(By.XPATH, '/html/body/main/div[4]/div/div/div/div/div/div/div[3]/form/div[8]/div[2]/div/select')
    selection_type_personne.send_keys(person_type)

def select_exhibition(web, exposition):
    exposition_collection_visiter = web.find_element(By.XPATH, '/html/body/main/div[4]/div/div/div/div/div/div/div[3]/form/div[4]/div[2]/input')
    exposition_collection_visiter.send_keys(f'{exposition}')

def select_date(web, jour):
    date = web.find_element(By.XPATH, '/html/body/main/div[4]/div/div/div/div/div/div/div[3]/form/div[5]/div[2]/input')
    date.send_keys(f'{jour}')

def select_time(web, time):
    heure_de_visite = web.find_element(By.XPATH, '//*[@id="form_f334"]')
    heure_de_visite.send_keys(f'{time}')

def select_responsable(web, responsable):
    nom_responsable_groupe = web.find_element(By.XPATH, '//*[@id="form_f24"]')
    nom_responsable_groupe.send_keys(f'{responsable}')

def select_phone(web, phone):
    telephone = web.find_element(By.XPATH, '//*[@id="form_f18"]')
    telephone.send_keys(f'{phone}')
    
def select_mail(web, mail):
    adresse_electronique = web.find_element(By.XPATH, '//*[@id="form_f21"]')
    adresse_electronique.send_keys(f'{mail}')
    
def select_etablissement(web, etablissement):
    nom_etablissement = web.find_element(By.XPATH, '//*[@id="form_f12"]')
    nom_etablissement.send_keys(etablissement)
    
def select_rue(web, rue):
    adresse = web.find_element(By.XPATH, '//*[@id="form_f14"]')
    adresse.send_keys(f'{rue}')   
    
def select_code(web, code):
    code_postal = web.find_element(By.XPATH, '//*[@id="form_f15"]')
    code_postal.send_keys(f'{code}')
    
def select_city(web, city):
    ville = web.find_element(By.XPATH, '//*[@id="form_f16"]')
    ville.send_keys(f'{city}')

def select_state(web, state):
    pays = web.find_element(By.XPATH, '//*[@id="form_f17"]')
    pays.send_keys(f'{state}')

def click_next(web, path):
    suivant_button = web.find_element(By.XPATH, path)
    suivant_button.click()

def click_validation(web, xpath):
    validation_button = web.find_element(By.XPATH, xpath)
    validation_button.click()
    
def click_send(web, send):
    send_button = web.find_element(By.XPATH, send)
    send_button.click()
    
def confirm(confirmation):
    print(f'{confirmation}')


# In[ ]:


def demander_reservation(url):
    web = webdriver.Chrome()
    web.get(url)

    musees_visiter = input("Quel musée voulez vous visiter parmi les suivants :\nMusée Archéologique: 1\nMusée arts décoratifs: 2\nMusée beaux arts: 3\nGalerie Heitz : 4\nMusée de lʼOeuvre Notre-Dame : 5\nMusée Historique de la Ville de Strasbourg : 6\nMusée Alsacien : 7\nMusée Tomi Ungerer : 8\nMusée dʼArt moderne et contemporain : 9\nAubette 1928 : 10\nMusée Zoologique : 11\nPôle dʼétude et de conservation : 12\n ... \n")
    select_museum(web, musees_visiter)

    type_de_groupe = input("Vous voulez réserver pour quel type de groupe:\nGroupe autonome: 1\nGroupe accueilli, public scolaire et structure de loisirs: 2\n... \n")
    select_group_type(web, type_de_groupe)

    nombre_de_personnes = input("Entrer le nombre de personnes:(max 35) \n... \n")
    select_number_of_people(web, nombre_de_personnes)

    sleep(3)

    person_type = input("Sélectionnez le type de public :\n ... \n")
    select_type_of_person(web, person_type)

    click_next(web, '//*[@id="rub_service"]/form/div[13]/div[1]/div/button')

    exposition = input("Vous pouvez entrer les expositions ou les collections que vous souhaitez voir : \n... \n")
    select_exhibition(web, exposition)

    jour = input("Entrer la jour que vous voulez réserver sous le format JJ/MM/YYYY : \n... \n")
    select_date(web, jour)

    time = input("Entrer l'heure que vous voulez réserver \n (Attention écrivez le sous le format 14:30) : \n... \n")
    select_time(web, time)

    click_next(web, '/html/body/main/div[4]/div/div/div/div/div/div/div[3]/form/div[8]/div[1]/div/button')
    
    responsable = input("Entrer le nom et prénom du résponsable du groupe :  \n... \n")
    select_responsable(web, responsable)
    
    phone =  input("Entrer un numéro de téléphone :  \n... \n")
    select_phone(web, phone)
    
    mail = input("Entrer un adresse email :  \n... \n")
    select_mail(web, mail)
    
    etablissement = input("Entrer le nom de votre établissement :  \n... \n")
    select_etablissement(web, etablissement)
    
    rue = input("Entrer l'adresse de l'établissement :  \n... \n")
    select_rue(web, rue)
    
    code = input("Entrer le code postale de l'établissement :  \n... \n")
    select_code(web, code)
    
    city = input("Entrer la ville de l'établissement :  \n... \n")
    select_city(web, city)
    
    state = input("Entrer le pays de l'établissement :  \n... \n")
    select_state(web, state)

    
    click_next(web, '//*[@id="rub_service"]/form/div[14]/div[1]/div/button')
    
   
    click_validation(web, '//*[@id="rub_service"]/form/div[3]/div/label/span[1]')

    click_send(web, '//*[@id="rub_service"]/form/div[5]/div[1]/div/button')
    
    
    confirm('Votre réservation à été bien prise en compte.\nVeuillez trouver le récapitulatif de votre demande dans votre boite mail. ')


# In[ ]:


#to call the code above :


# In[ ]:


demander_reservation('https://demarches.strasbourg.eu/culture-loisirs/musees-reservation-groupe/')

