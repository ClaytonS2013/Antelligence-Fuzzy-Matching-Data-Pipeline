import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def main():
    # put your real logic here (read SQL from ./sql, call APIs, etc.)
    print("Pipeline starting…")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY")
    print("Connected to Supabase at:", SUPABASE_URL)
    print("All done!")

if __name__ == "__main__":
    main()
