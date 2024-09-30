db = db.getSiblingDB('films_db');  // crée la table films_db et switch sur la table
db.films_mongo.insertMany([
  { 
    _id: 1,
    original_title: "Insidious: Chapter 3", 
    budget: 10000000, 
    revenue: 104303851, 
    runtime: 97.0, 
    vote_count: 983, 
    evaluation: "moyen"
  },
  { 
    _id: 2, 
    budget: 10000000,
    original_title: "The Last Dragon",
    revenue: 25754284, 
    runtime: 108.0, 
    vote_count: 69, 
    evaluation: "moyen"
  },
  { 
    _id: 3, 
    budget: 10000000, 
    original_title: "The Lawnmower Man",
    revenue: 32101000, 
    runtime: 108.0, 
    vote_count: 197, 
    evaluation: "moyen"
  },
  { 
    _id: 4, 
    budget: 9000000,
    original_title:"Nick and Norah's Infinite Playlist", 
    revenue: 32973937, 
    runtime: 89.0, 
    vote_count: 379, 
    evaluation: "moyen"
  },
  { 
    _id: 5, 
    budget: 10000000, 
    original_title: "Dogma",
    revenue: 30652890, 
    runtime: 130.0, 
    vote_count: 823, 
    evaluation: "moyen"
  },
]);
