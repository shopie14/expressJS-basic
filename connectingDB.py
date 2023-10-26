from pymongo import MongoClient

# fungsi koneksi ke database
def connectingDB():
    # inisialisasi database
    mongo_host = 'database2.pptik.id'
    mongo_user = 'magangitg'
    mongo_pws = 'bWFnYW5naXRn'
    mongo_db = 'magangitg'

    try:
        # Create a MongoClient instance
        client = MongoClient('mongodb://magangitg:bWFnYW5naXRn@database2.pptik.id:27017/?authMechanism=DEFAULT&authSource=magangitg')
        db = client['magangitg']
        collection = db['face_lskk']

        # Test the connection by listing the database names
        database_names = collection.list_database_names()

        if mongo_db in database_names:
            # The database exists, so it's successfully connected
            print('Berhasil terkoneksi ke database')
            db = client[mongo_db]  # Get the database
            return db
        else:
            # The specified database does not exist
            print(f'Gagal terkoneksi ke database. Database "{mongo_db}" not found.')
            return None

    except Exception as e:
        # Handle any connection errors here
        print(f'Gagal terkoneksi ke database: {str(e)}')
        return None

# Example usage:
if __name__ == '__main__':
    db_connection = connectingDB()
