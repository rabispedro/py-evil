from bs4 import BeautifulSoup, Tag
import pandas
import requests
from requests import Response
from time import gmtime, sleep, strftime
from typing import Optional
import os

BASE_URL: str = "https://www.residentevildatabase.com"
HEADERS: dict = {
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
	'Accept': '*/*',
	'Origin': 'https://www.residentevildatabase.com',
	'Connection': 'keep-alive',
	'Referer': 'https://www.residentevildatabase.com/',
	'Sec-Fetch-Dest': 'empty',
	'Sec-Fetch-Mode': 'cors',
	'Sec-Fetch-Site': 'cross-site',
}
POOLING_SECONDS: float = 0.875

def extract_characters_list() -> list[str]:
	characters: list[str] = []

	try:
		response: Response = requests.get((BASE_URL + "/personagens"), headers=HEADERS)

		if response.status_code >= 200 and response.status_code < 300:
			page = BeautifulSoup(response.text, features="html.parser")
			body: Optional[Tag] = page.find("div", class_="td-page-content")

			if body is not None:
				for tag in body.find_all("a"):
					characters.append(tag.get('href').split("/")[-2])
		else:
			print(f"Ocorreu algum erro na obtenção do personagem: {character}\nStatus code: {response.status_code}")
	finally:
		print(f"Finalizado a extração de {len(characters)} personagens.")

	return characters

def extract_characters_info(character: str) -> dict:
	result: dict = {}
	try:
		response: Response = requests.get((BASE_URL + "/personagens/" + character), headers=HEADERS)

		if response.status_code >= 200 and response.status_code < 300:
			page: BeautifulSoup = BeautifulSoup(response.text, features="html.parser")
			body: Optional[Tag] = page.find("div", class_="td-page-content")

			if body is not None:
				image_tag = body.find("img")
				result["image"] = image_tag.get("href")

				for tag in body.find_all("p")[1].find_all("em"):
					key, value, *_ = tag.text.split(":")
					result[key.strip()] = value.strip()

				feat_key: str = body.find("h4")
				feat_list = body.find("h4").find_next().find_all("li")
				result[feat_key] = [tag.text.replace("/", "").strip() for tag in feat_list]
		else:
			raise RuntimeError(f"Ocorreu algum erro na obtenção do personagem: {character}\nStatus code: {response.status_code}")
	except RuntimeError:
		return {}
	finally:
		print(f"Finalizado a extração de informações do personagem '{character}'.")

	return result

def save_to_file(data: dict, path: str, name: str) -> None:
	today: str = strftime("%m-%d-%Y", gmtime())
	now: str = strftime("%H:%M:%S", gmtime())

	file_name: str = (now + "-" + name)

	complete_path: str = os.path.join(path, today)
	complete_file_name: str = os.path.join(complete_path, file_name)

	if not os.path.exists(complete_path):
		os.makedirs(complete_path, exist_ok=True)

	try:
		data_frame: pandas.DataFrame = pandas.DataFrame(data)
		data_frame.to_csv((complete_file_name + ".csv"), index=False, sep=";")
		data_frame.to_json((complete_file_name + ".json"), index=False)
	finally:
		print(f"Finalizado a escrita no arquivo: '{complete_file_name}'")

	return None

if __name__ == "__main__":
	print(f"Start Web Scraping on '{BASE_URL}'")

	characters: list[str] = extract_characters_list()
	infos: dict = {}

	for character in characters:
		sleep(POOLING_SECONDS)
		infos[character] = extract_characters_info(character)

	save_to_file(infos, "data", "result")
