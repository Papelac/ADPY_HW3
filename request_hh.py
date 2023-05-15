import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import re
import json
import os

headers = Headers(browser='edge', os='win', headers='Content-Type": "application/json; charset=utf-8')
parses_data = []

#проверка на вхождение внутри отрабатывает, но если считывать по всем 40 страницам, попадаю на проверку робота,
# из-за этого условие на вхождение Django и Flask сейчас включено в ссылку
#html_data = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&page=0', headers=headers.generate()).text
#html_data = requests.get('https://spb.hh.ru/search/vacancy?text=python+django+flask&area=1&area=2&page=0, headers=headers.generate()).text

number_of_page = 0
while True:
#while number_of_page < 1:
    html_data = requests.get(f'https://spb.hh.ru/search/vacancy?text=python+django+flask&area=1&area=2&page={number_of_page}]', headers=headers.generate())
    if html_data.status_code != 200:
        break
    
    number_of_page +=1
        
    soup = BeautifulSoup(html_data.text, 'lxml')

    tag_all_vacancy_on_page = soup.find('main', class_='vacancy-serp-content')

    tags_vacancies = tag_all_vacancy_on_page.find_all('div', class_='serp-item')

    for tag_vacancies in tags_vacancies:
        h3_tag = tag_vacancies.find('h3')
        a_tag = h3_tag.find('a')
        title = a_tag.text
        #print(title)
        link = a_tag['href']
        #print(link)
        
        try:
            salary = tag_vacancies.find(attrs={"data-qa": "vacancy-serp__vacancy-compensation"}).text
        except:
            salary = 'з/п не указана'   
        town = tag_vacancies.find('div', attrs={"data-qa": "vacancy-serp__vacancy-address"}).text
        company = tag_vacancies.find('a', attrs={"data-qa": "vacancy-serp__vacancy-employer"}).text
        
        vacancy_description_soup = BeautifulSoup(requests.get(link, headers=headers.generate()).text, 'lxml')
        tag_vacancy_description = vacancy_description_soup.find('div', class_='vacancy-description')
        tag_description = tag_vacancy_description.find('div', attrs={"data-qa": "vacancy-description"})
        description = tag_description.text
        tag_skills = tag_vacancy_description.find('div', class_='bloko-tag-list')
        if tag_skills is None:
            skills = ''
        else:
            skills = tag_skills.text
        
        word_search_1 = 'Django|django|Джанго|джанго'
        word_search_2 = 'Flask|flask|Фласк|фласк'
        
        pattern1 = r"Django|django|Джанго|джанго"
        pattern2 = r"Flask|flask|Фласк|фласк"
        pattern_salary = r"USD"
        
        result1 = bool(re.search(pattern1, description))
        result1_dop = bool(re.search(pattern1, skills))
        result2 = bool(re.search(pattern2, description))
        result2_dop = bool(re.search(pattern2, skills))
        result_salary = bool(re.search(pattern_salary, salary))
            
        #if (result1 or result1_dop) and (result2 or result2_dop) and result_salary:
        if (result1 or result1_dop) and (result2 or result2_dop):
            
            parses_data.append(
                {
    #                'title': title,
                    'link': link,
    #                'description': description,           
                    'salary': salary,
                    'company': company,
                    'town': town
                }
            )

#print(parses_data)
current = os.getcwd()
vacation_file_name = 'vacation_python.txt'
new_full_path = os.path.join(current, vacation_file_name)
with open(new_full_path, "w", encoding="utf-8") as f:
    json.dump(parses_data, f, ensure_ascii=False, indent=4)


