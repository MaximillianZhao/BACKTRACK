from src.services.musicbrainz_client import find_artist_mbid, get_tribute_artists_for_original

def main():
    original = "David Bowie"
    mbid = find_artist_mbid(original)
    print(f"{original} MBID:", mbid)

    if not mbid:
        print("Could not find the artist MBID.")
        return

    tributes = get_tribute_artists_for_original(mbid)
    print("Found tributes:", len(tributes))
    for t in tributes[:10]:
        print("-", t["name"], t["mbid"])

if __name__ == "__main__":
    main()