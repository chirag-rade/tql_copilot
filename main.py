import streamlit as st
from openai import OpenAI
import json
import os
GroupsNew = [
    {
        "EDI": ["N*", "B2A", "B2", "L3", "AT8", "ST", "ISA","L11", "LH", "PLD",  "GS","SE"], 
        "JSON": [
            "CorrelationId", "ApplicationType", "CustomerPo", "RateQualifier", "SCAC",
            "TruckOrderedNotUsed", "Weight", "WeightQualifier", "TotalAdvance",
            "TotalCharge", "TotalPallets", "TotalPrePaid", "ShipmentId", "FreightRate",
            "FreightTerm", "LadingQuantity", "LegacyCustomerID", "LegacyTPProfileID", "EdiProperties",
            "Equipment"
        ],
    
    },
    {
        "EDI": ["K1", "L11", "NTE", "L3", "ISA",  "AT8"],
        "JSON": [
            "TqlLoadInfo", "ArchiveFiles", "LoadAddresses", "LoadPalletExchange",
            "LoadReferenceNumbers", "LoadRemarks"
        ],
       
    },
    {
        "EDI": [ "B2A", "B2", "L3", "AT8", "ST", "ISA","L11", "LH", "PLD"], 
        "JSON": [
            "TruckOrderedNotUsed",  "TotalAdvance", "TotalPallets", "TotalPrePaid", 
            "LegacyCustomerID", "LegacyTPProfileID"
        ],

    },
]
st.title('TQL copilot')
platform = st.selectbox('Select EDI format', ['204', '210', '214', '990'])
llm = st.selectbox('Select model', ['gpt-4-1106-preview', 'gpt-3.5-turbo-1106'])

question = st.text_input('Ask your question here')

def get_openai_response(question, model, platform):
    # Find the list of JSON fields for the given EDI identifier
    json_fields = []
    all_json_fields_combined = []
    for group in GroupsNew:
        all_json_fields_combined.extend(group["JSON"])
        if question in group["EDI"]:
            json_fields.extend(group["JSON"])
    
    # Remove duplicates by converting the list to a set and back to a list
    json_fields = list(set(json_fields))
    all_json_fields_combined = list(set(all_json_fields_combined))

    # Set the content for the 'user' role based on whether the question is found
    if json_fields:
        user_content = f"Pick the json key for this EDI key '{question}'? Pick the best suited from this list of json keys: {json_fields}."
    else:
        user_content = f"{question} is not found. Here are all the json fields you can choose from: {all_json_fields_combined}."

    client = OpenAI(api_key="")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"Answer the following question about EDI format {platform}"
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        temperature=0,
        max_tokens=4095,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

if st.button('Submit'):
    # Updated logic to handle the question and platform using OpenAI API.
    result = get_openai_response(question, llm, platform)
   
    # Save question and result in messages and ensure it stays when Streamlit reloads
    messages = st.session_state.get('messages', [])
    messages.append({"Human": question})
    messages.append({"AI": result})
    
    st.session_state['messages'] = messages
    for message in messages:
        for role, text in message.items():
            with st.container():
                st.markdown(f"**{role}** : {text}", unsafe_allow_html=True)

if st.button('Clear Messages'):
    st.session_state['messages'] = []