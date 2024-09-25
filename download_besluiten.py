import requests
from io import BytesIO


# Base URLs for API requests
besluiten_base_url = "https://besluiten.onroerenderfgoed.be/besluiten"

# Headers for JSON requests
headers_json = {
    "Accept": "application/json"
}


# Function to get detailed information from the provided 'aanduidingsobjecten' URL
def get_aanduidingsobjecten_details(aanduidingsobject_url):
    response = requests.get(aanduidingsobject_url, headers=headers_json)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching details for {aanduidingsobject_url}: {response.status_code}")
        return None


# Function to fetch the besluiten (decisions) for a specific besluit ID
def fetch_besluit_files(besluit_id):
    url = f"{besluiten_base_url}/{besluit_id}/bestanden/"
    response = requests.get(url, headers=headers_json)

    if response.status_code == 200:
        return response.json()  # Assuming JSON response with file metadata
    else:
        print(f"Error fetching files for besluit {besluit_id}: {response.status_code}")
        return None


# Function to download PDF files
def download_pdf(file_id, besluit_id):
    # Construct the final URL for downloading the file
    file_url = f"{besluiten_base_url}/{besluit_id}/bestanden/{file_id}"
    print(f"Attempting to download from URL: {file_url}")

    response = requests.get(file_url, stream=True)

    if response.status_code == 200:
        print(f"Downloaded {file_id}")
        bytes_buffer = BytesIO(response.content)
        return bytes_buffer
    else:
        print(f"Error downloading PDF file {file_id}: {response.status_code} - {response.text}")


# Main function to process a given aanduidingsobject URL and download besluiten PDFs
def process_aanduidingsobject_url(aanduidingsobject_url):
    # Step 1: Get detailed info from the given URL
    obj_details = get_aanduidingsobjecten_details(aanduidingsobject_url)
    if obj_details:
        # Extract location and relevant metadata
        object_metadata = {
            "aanduidingsobject_url": aanduidingsobject_url,
            "object_id": obj_details.get("id"),
            "location": obj_details.get("locatie_samenvatting", "N/A"),  # Location summary
            "besluiten": []
        }

        # Step 2: Extract 'besluiten' (decisions) from the object details
        relevant_besluiten = obj_details.get("besluiten", [])

        pdf_bytes_buffers: list[BytesIO] = []

        for besluit in relevant_besluiten:
            besluit_id = besluit.get("id")
            besluit_date = besluit.get("datum_ondertekening", "N/A")  # Extract the signing date
            besluit_titel = besluit.get("Onderwerp", "N/A")  # Extract the signing date

            print(f"Fetching besluit ID {besluit_id}")

            # Step 3: Fetch the files for each besluit
            besluit_files = fetch_besluit_files(besluit_id)

            if besluit_files:
                for file in besluit_files:
                    file_id = file.get("id")
                    file_type = file.get("bestandssoort", {}).get("soort", "")

                    if file_type == "Besluit":  # Only download files of type "Besluit"
                        print(f"Downloading PDF file ID {file_id} for besluit {besluit_id}")
                        pdf_bytes_buffer = download_pdf(file_id, besluit_id)
                        if pdf_bytes_buffer is not None:
                            pdf_bytes_buffers.append(pdf_bytes_buffer)

                        # Add decision metadata for JSON
                        besluit_metadata = {
                            "besluit_url": f"{besluiten_base_url}/{besluit_id}",
                            "besluit_pdf_url": f"{besluiten_base_url}/{besluit_id}/bestanden/{file_id}",
                            "besluit_id": besluit_id,
                            "pdf_file_id": file_id,
                            "besluit_date": besluit_date,
                            "besluit_titel": besluit_titel
                        }
                        object_metadata["besluiten"].append(besluit_metadata)

        # Step 4: Save metadata as a JSON file
        # json_output_file = os.path.join(save_dir, f"metadata_{obj_details.get('id')}.json")

        # with open(f"/dbfs{json_output_file}", 'w', encoding='utf-8') as json_file:
        #     json.dump(object_metadata, json_file, ensure_ascii=False, indent=4)
        #     print(object_metadata)

        # print(f"Metadata saved to {json_output_file}")
        return {"meta": object_metadata, "buffers": pdf_bytes_buffers}
    else:
        print("No valid object details found.")
