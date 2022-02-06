import json
import requests
import pandas as pd
import argparse


def get_tokens(contract_address, start_after=None, limit=30):
    """Get Token IDs from a smart contract

    Args:
        contract_address ([string]): Contract address of an NFT
        start_after ([string], optional): Starting Token ID.Defaults to None.
        limit ([int], optional): Result limit. Defaults to 30.

    Returns:
        [list(string)]: Returns list of Token IDs from the smart contract
    """
    message = {"all_tokens": {"limit": limit}}
    if start_after:
        message["all_tokens"]["start_after"] = str(start_after)
    message_string = json.dumps(message)
    url = (
        f"https://fcd.terra.dev/wasm/contracts/{contract_address}/"
        f"store?query_msg={message_string}"
    )
    response = requests.get(url)
    tokens = response.json()["result"]["tokens"]
    return tokens


def get_all_tokens(contract_address):
    """Get all available Token IDs from a smart contract

    Args:
        contract_address ([string]): Contract address of an NFT

    Returns:
        [list(string)]: Returns full list of token ids
    """
    token_list = []
    start_after = None
    while True:
        tokens = get_tokens(contract_address, start_after)
        if not tokens:
            break
        start_after = tokens[-1]
        token_list = token_list + tokens
    return token_list


def get_nft_info(contract_address, token_id):
    """Get NFT information from a token ID

    Args:
        contract_address ([string]): Contract address of an NFT
        token_id ([string]): Token ID of a NFT collection

    Returns:
        [dict]: Returns a dictionary of NFT attributes for the token id
    """
    message = json.dumps({"nft_info": {"token_id": f"{token_id}"}})
    url = (
        f"https://fcd.terra.dev/wasm/contracts/{contract_address}/"
        f"store?query_msg={message}"
    )
    response = requests.get(url)
    extension = response.json()["result"]["extension"]
    for a in extension["attributes"]:
        extension[a["trait_type"]] = a["value"]
    return extension


def get_all_nft_info(contract_address):
    """Get all NFT attributes for an NFT collection

    Args:
        contract_address ([string]): Contract address of an NFT

    Returns:
        [list of dicts]: Returns a list of dict of all nft attributes
    """
    tokens = get_all_tokens(contract_address)
    num_tokens = len(tokens)
    print(f"number of tokens :{num_tokens}")
    t_count = 1
    nft_info_list = []
    for token in tokens:
        print(f"processed {t_count} / {num_tokens}")
        nft_info_list.append(get_nft_info(contract_address, token))
        t_count += 1
    return nft_info_list


def calculate_rarity(row, attribute_types):
    """Helper function to calculate rarity for each row in a pandas dataframe.
       Uses rarity.tools scoring

    Args:
        row ([pandas row]): row of a pandas dataframe
        attribute_types ([list]): list of attributes for the nft collection

    Returns:
        [int]: Rarity score for the nft
    """
    score = 0
    for attribute in attribute_types:
        score = score + 1 / row[f"{attribute}_probability"]
    return score


def create_nft_df(nft_info_list):
    """Converts the list of NFT attributes into a dataframe
       and includes rarity information

    Args:
        nft_info_list ([list]): List of attributes based on get_all_nft_info

    Returns:
        [pandas dataframe]: Dataframe of NFT information
    """
    for j in nft_info_list:
        ipfs_id = j["image"].replace("ipfs://", "")
        j["ipfs_url"] = f"https://cf-ipfs.com/ipfs/{ipfs_id}"
        for a in j["attributes"]:
            j[a["trait_type"]] = a["value"]
    df = pd.DataFrame(nft_info_list)
    attribute_types = [x["trait_type"] for x in df["attributes"][0]]
    attribute_prob_df_dict = {}
    for attribute in attribute_types:
        attribute_df = (
            df[attribute]
            .value_counts(dropna=False)
            .rename_axis(attribute)
            .reset_index(name=f"{attribute}_count")
        )
        attribute_df[f"{attribute}_probability"] = (
            attribute_df[f"{attribute}_count"]
            / attribute_df[f"{attribute}_count"].sum()
        )
        attribute_prob_df_dict[attribute] = attribute_df
    for attribute in attribute_types:
        df = df.merge(
            attribute_prob_df_dict[attribute],
            how="left",
            on=attribute)
    df["rarity_score"] = df.apply(
        lambda x: calculate_rarity(x, attribute_types), axis=1
    )
    df = df.sort_values("rarity_score", ascending=False)
    df["rarity_rankings"] = range(1, len(df) + 1)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--contract", type=str, required=True)
    args = parser.parse_args()
    contract = args.contract

    nft_info_list = get_all_nft_info(contract)
    df = create_nft_df(nft_info_list)
    df.to_csv(f"{contract}_nft.csv", index=None)