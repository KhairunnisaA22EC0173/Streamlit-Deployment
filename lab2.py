import pandas as pd
import requests
import streamlit as st
import networkx as nx 
import matplotlib.pyplot as plt

def retrieve_ppi_biogrid(target_protein):
    url = f"https://webservice.thebiogrid.org/interaction/102009/?format=json&accessKey=35b4325d8fc43d2a024c8f95f8d1772e"
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame()  # Return empty DataFrame if request fails
    
    data = response.json()
    interactions = []
    for interaction in data.values():
        interactions.append({
            "Interactor_A": interaction["OFFICIAL_SYMBOL_A"],
            "Interactor_B": interaction["OFFICIAL_SYMBOL_B"],
            "Experimental_System": interaction["EXPERIMENTAL_SYSTEM"],
            "Pubmed_ID": interaction["PUBMED_ID"]
        })
    
    return pd.DataFrame(interactions)

def retrieve_ppi_string(target_protein):
    url = f"https://string-db.org/api/json/network"
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame()
    
    # Parse the TSV response into a DataFrame
    data = pd.read_csv(pd.compat.StringIO(response.text), sep="\t")
    interactions = data[["preferredName_A", "preferredName_B", "score"]]
    interactions.rename(columns={"preferredName_A": "Interactor_A", "preferredName_B": "Interactor_B"}, inplace=True)
    return interactions

def generate_network(dataframe):
    graph = nx.Graph()
    for _, row in dataframe.iterrows():
        graph.add_edge(row['Interactor_A'], row['Interactor_B'])
    return graph

def get_centralities(network_graph):
    centralities = {
        "Degree Centrality": nx.degree_centrality(network_graph),
        "Betweenness Centrality": nx.betweenness_centrality(network_graph),
        "Closeness Centrality": nx.closeness_centrality(network_graph),
        "Eigenvector Centrality": nx.eigenvector_centrality(network_graph),
        "PageRank": nx.pagerank(network_graph)
    }
    return centralities

def main():
    st.title("Lab 2 - KHAIRUNNISA BINTI ROSLAN")
    
    protein_id = st.text_input("Enter Protein ID:")
    database = st.selectbox("Choose Database", ["BioGRID", "STRING"])
    
    if st.button("Retrieve PPI"):
        with st.spinner("Retrieving PPI data..."):
            if database == "BioGRID":
                ppi_data = retrieve_ppi_biogrid(protein_id)
            else:
                ppi_data = retrieve_ppi_string(protein_id)
            
            if ppi_data.empty:
                st.error("No data found!")
                return
            
            # Generate network
            network = generate_network(ppi_data)
            
            # Split into two columns
            col1, col2 = st.columns(2)
            
            # Column 1: PPI Data
            with col1:
                st.subheader("PPI Data Information")
                st.dataframe(ppi_data)
                st.write(f"**Number of Nodes:** {network.number_of_nodes()}")
                st.write(f"**Number of Edges:** {network.number_of_edges()}")
                st.graphviz_chart(nx.nx_pydot.to_pydot(network).to_string())
            
            # Column 2: Centrality Measures
            with col2:
                st.subheader("Centrality Measures")
                centralities = get_centralities(network)
                for name, values in centralities.items():
                    st.markdown(f"**{name}:**")
                    st.write(pd.DataFrame.from_dict(values, orient='index', columns=[name]))
                    
if __name__ == "__main__":
    main()



