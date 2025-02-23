import time
from datetime import datetime
from xml.etree import ElementTree as ET
from Bio import Entrez
from app.config import Config


def fetch_pubmed_ids(query, total_results=2000, batch_size=500, mindate=None, maxdate=None):
    """Fetch PubMed article IDs matching the query with pagination and date filtering."""
    all_ids = []
    Entrez.email = Config.ENTREZ_EMAIL
    Entrez.api_key = Config.ENTREZ_API_KEY
    for start in range(0, total_results, batch_size):
        print(f"Fetching IDs {start+1} to {min(start+batch_size, total_results)}")
        try:
            handle = Entrez.esearch(
                db="pubmed", term=query, retmax=batch_size, retstart=start,
                mindate=mindate, maxdate=maxdate, datetype="pdat",
                api_key=Entrez.api_key, email=Entrez.email
            )
            record = Entrez.read(handle)
            ids = record['IdList']
            handle.close()
            all_ids.extend(ids)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching IDs: {e}")
            break
    # print(f"all_ids:\n")
    # print(*all_ids)

    return all_ids

def fetch_pubmed_data(pubmed_ids, mindate=None, maxdate=None):
    """Fetch titles, abstracts, and publication dates for the given PubMed IDs."""
    articles = []
    if len(pubmed_ids) <= Config.MAX_FETCH_IDS:
        id_string = ",".join(pubmed_ids)
        # articles.extend(parse_pubmed_data(id_string, pubmed_ids))
        articles.extend(parse_pubmed_data(id_string, mindate, maxdate))
    else:
        for i in range(0, len(pubmed_ids), Config.BATCH_SIZE):
            batch_ids = pubmed_ids[i:i+ Config.BATCH_SIZE]
            id_string = ",".join(batch_ids)
            # articles.extend(parse_pubmed_data(id_string, batch_ids))
            articles.extend(parse_pubmed_data(id_string, mindate, maxdate))
            time.sleep(0.5)
    return articles

def parse_date(date_string):
    """Helper function to parse dates with different formats."""
    date_string = date_string.replace("/", "-")  # Normalize date format to use '-'
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    raise ValueError(f"Date format not recognized: {date_string}")
    
   
def extract_date(date_element):
    if date_element is not None:
        year = date_element.find("Year").text if date_element.find("Year") is not None else None
        month = date_element.find("Month").text if date_element.find("Month") is not None else None
        day = date_element.find("Day").text if date_element.find("Day") is not None else None

        if year:
            try:
                # Convert year, month, and day to integers if available
                year = int(year)
                if month and not month.isdigit():
                    try:
                        month = datetime.strptime(month, "%b").month
                    except ValueError:
                        month = None
                else:
                    month = int(month) if month and month.isdigit() else None

                day = int(day) if day and day.isdigit() else None

                # Return date with the most information available
                return {
                    "year": year,
                    "month": month,
                    "day": day
                }
            except ValueError:
                return None
    return None

def compare_dates(date1, date2):
    """Compare two dates element by element and return the earlier date."""
    if not date1:
        return date2
    if not date2:
        return date1

    # Compare year first
    if date1["year"] != date2["year"]:
        return date1 if date1["year"] < date2["year"] else date2

    # If years are the same, compare month
    if date1["month"] and date2["month"]:
        if date1["month"] != date2["month"]:
            return date1 if date1["month"] < date2["month"] else date2
    elif date1["month"]:
        return date1
    elif date2["month"]:
        return date2

    # If months are the same, compare day
    if date1["day"] and date2["day"]:
        if date1["day"] != date2["day"]:
            return date1 if date1["day"] < date2["day"] else date2
    elif date1["day"]:
        return date1
    elif date2["day"]:
        return date2

    # If all elements are equal or missing, return the first date
    return date1

def parse_pubmed_data(id_string, mindate, maxdate):
    """Fetch and parse PubMed data (PubMed ID, title, abstract, and date) with date filtering."""
    from xml.etree import ElementTree as ET
    articles = []
    Entrez.email = Config.ENTREZ_EMAIL
    Entrez.api_key = Config.ENTREZ_API_KEY
    # mindate=Config.MINDATE
    # maxdate=Config.MAXDATE

    try:
        fetch_handle = Entrez.efetch(
            db="pubmed", id=id_string, retmode="xml",
            api_key=Entrez.api_key, email=Entrez.email
        )
        data = fetch_handle.read()
        fetch_handle.close()

        root = ET.fromstring(data)
        for article in root.findall(".//PubmedArticle"):
            pubmed_id = article.find(".//PMID").text
            title = article.find(".//ArticleTitle")
            abstract = article.find(".//AbstractText")
            journal = article.find(".//Journal/Title")

            # Extract publication date fields
            article_date = article.find(".//ArticleDate")
            pub_date = article.find(".//PubDate")

            
           # Parse dates
            article_date_obj = extract_date(article_date)
            pub_date_obj = extract_date(pub_date)

            # Determine the earliest date
            final_date_obj = compare_dates(article_date_obj, pub_date_obj)

            # Skip if no valid date is found
            if not final_date_obj:
                continue

            # Construct a datetime object for filtering
            year = final_date_obj["year"]
            month = final_date_obj["month"] if final_date_obj["month"] else 1
            day = final_date_obj["day"] if final_date_obj["day"] else 1
            final_date = datetime(year, month, day)

            # Apply filtering based on mindate and maxdate
            if mindate:
                mindate_obj = datetime.strptime(mindate, "%Y/%m/%d")
                if final_date < mindate_obj:
                    continue

            if maxdate:
                maxdate_obj = datetime.strptime(maxdate, "%Y/%m/%d")
                if final_date > maxdate_obj:
                    continue

            # Add article to the list if it passes the date filter
            articles.append({
                "pubmed_id": pubmed_id,
                "title": title.text if title is not None else "N/A",
                "abstract": abstract.text if abstract is not None else "N/A",
                "journal": journal.text if journal is not None else "N/A", 
                "date": final_date.strftime("%Y/%m/%d")
            })

    except Exception as e:
        print(f"Error fetching or parsing data: {e}")

    return articles