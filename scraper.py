import requests
import lxml.html
import pandas as pd

class Scraper:
    def __init__(self):
        self.va_list = self.load_cities()
        self.service_indexes = self.generate_service_list()
        
    def generate_service_list(self):
        ending = "/services/index.asp"
        service_indexes = []
        for facility in self.va_list:
            service_indexes.append(facility+ending)
        return [elem for elem in service_indexes if elem.startswith("http")]
               
    def load_cities(self):
        with open("va_list.txt","r") as f:
            return f.read().split("\n")

    def clean(self,string):
        return unicode(string).replace("\r","").replace("\n","").replace("\t","").strip().encode("ascii","ignore")

    #ToDo add full url name
    def generate_services_csv(self):
        tmp = {}
        df = pd.DataFrame()
        for va_facility in self.service_indexes:
            html = lxml.html.fromstring(requests.get(va_facility).text)
            service_names = [elem.text_content() for elem in html.xpath('//td[@headers="srv"]//a')]
            links = html.xpath('//td[@headers="srv"]//a/@href')
            locations = [elem.text_content() for elem in html.xpath('//td[@headers="loc"]')]
            phones = [elem.text_content() for elem in html.xpath('//td[@headers="ph"]')]
            descriptions = [elem.text_content() for elem in html.xpath('//td[@headers="srv"]//span')]
            va_fac = va_facility.split("http://")[1].split(".va")[0]
            for ind,val in enumerate(service_names):
                tmp["service_name"] = self.clean(val)
                tmp["link"] = self.clean(links[ind])
                tmp["location"] = self.clean(locations[ind])
                tmp["phone"] = self.clean(phones[ind])
                tmp["description"] = self.clean(descriptions[ind])
                tmp["va_facility"] = self.clean(va_fac)
                df = df.append(tmp,ignore_index=True)
        df.to_csv("services_list.csv")

if __name__ == '__main__':
    s = Scraper()
    s.generate_services_csv()
