from mongo_connection import MongoAccess

class Data_mongo:
    def __init__(self):
        self.mongo = MongoAccess()
        self.mongo.connexion()

    def get_films_data_mongo(self):
        films = self.mongo.collection.find()
        films_list = []
        for film in films:
            film_data = {
                "original_title": film.get("original_title"),
                "budget": film.get("budget"),
                "revenue": film.get("revenue"),
                "runtime": film.get("runtime"),
                "vote_count": film.get("vote_count"),
                "evaluation": film.get("evaluation")
            }
            films_list.append(film_data)
        self.mongo.deconnexion()
        return films_list


