import requests
import lxml.html
import pandas as pd
import math
from scipy import stats
import scipy as sp

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
            base_name = "/".join(va_facility.split("/")[:-1])
            html = lxml.html.fromstring(requests.get(va_facility).text)
            service_names = [elem.text_content() for elem in html.xpath('//td[@headers="srv"]//a')]
            links = [base_name+"/"+elem.split("/")[-1] for elem in html.xpath('//td[@headers="srv"]//a/@href')]
            locations = [elem.text_content() for elem in html.xpath('//td[@headers="loc"]')]
            phones = [elem.text_content() for elem in html.xpath('//td[@headers="ph"]')]
            descriptions = [elem.text_content() for elem in html.xpath('//td[@headers="srv"]//span')]
            va_fac = va_facility.split("http://")[1].split(".va")[0].split("www.")[1]
            for ind,val in enumerate(service_names):
                tmp["service_name"] = self.clean(val)
                tmp["link"] = self.clean(links[ind])
                tmp["location"] = self.clean(locations[ind])
                tmp["phone"] = self.clean(phones[ind])
                tmp["description"] = self.clean(descriptions[ind])
                tmp["va_facility"] = self.clean(va_fac)
                df = df.append(tmp,ignore_index=True)
        df.to_csv("services_list.csv")

class ServiceAnalyzer:
    def __init__(self):
        self.df = pd.read_csv("services_list.csv")
        self.service_counts = self.services_count()
        
    def services_count(self):
        counts = []
        for i in self.df.index:
            va_facility = self.df.ix[i]["va_facility"]
            counts.append(va_facility)
        counts = {elem:counts.count(elem) for elem in counts}
        with open("services_count.txt","w") as f:
            for place in counts.keys():
                f.write(place+" has "+str(counts[place])+" services available.\n") 
            
        return counts
    
    def descriptive_statistics(self):
        s = sp.array(self.service_counts.values())
        n,min_max,mean,var,skew,kurt = stats.describe(s)
        with open("descriptive_statistics.txt","w") as f:
            f.write("The mean number of services was: " + str(round(mean,3)) + "\n")
            f.write("The standard deviation of the number of services offered was:" + str(round(math.sqrt(var)))+"\n")
        return {
            "n":n,
            "average":mean,
            "std_dev":math.sqrt(var),
            "skew":skew,
            "kurtosis":kurt
            }
    
    def output_service_names(self):
        services = pd.DataFrame()
        unique_names = []
        for i in self.df.index:
            services = services.append({"service_name":self.df.ix[i]["service_name"],"va_facility":self.df.ix[i]["va_facility"]},ignore_index=True)
            service = self.df.ix[i]["service_name"]
            if not service in unique_names:
                unique_names.append(service)
        services.to_csv("services.csv")
        data = ""
        for name in unique_names:
            data += name+"\n"
        with open("service_names.txt","w") as f:
            f.write(data)

    
if __name__ == '__main__':
    #s = Scraper()
    #s.generate_services_csv()
    sa = ServiceAnalyzer()
    print sa.services_count()
    print sa.descriptive_statistics()
    sa.output_service_names()
