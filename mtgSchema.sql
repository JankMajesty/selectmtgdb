-- enable foreign keys
PRAGMA foreign_keys = ON;

-- Artists
CREATE TABLE IF NOT EXISTS Artist (
  ArtistID   INTEGER PRIMARY KEY,
  ArtistName TEXT    NOT NULL
);

-- Rarities
CREATE TABLE IF NOT EXISTS Rarity (
  RarityID   INTEGER PRIMARY KEY,
  RarityName TEXT    NOT NULL
);

-- Sets
CREATE TABLE IF NOT EXISTS CardSet (
  SetID       INTEGER PRIMARY KEY,
  SetName     TEXT    NOT NULL,
  SetCode     TEXT    NOT NULL UNIQUE,
  ReleaseDate TEXT    NOT NULL  -- store as ISO yyyy-mm-dd
);

-- Colors
CREATE TABLE IF NOT EXISTS Color (
  ColorID INTEGER PRIMARY KEY,
  Color   TEXT    NOT NULL UNIQUE
);

-- Card Types
CREATE TABLE IF NOT EXISTS CardType (
  CardTypeID INTEGER PRIMARY KEY,
  TypeName   TEXT    NOT NULL UNIQUE
);

-- Subtypes
CREATE TABLE IF NOT EXISTS SubType (
  SubTypeID   INTEGER PRIMARY KEY,
  SubTypeName TEXT    NOT NULL UNIQUE
);

-- Cards
CREATE TABLE IF NOT EXISTS Card (
  CardID             INTEGER PRIMARY KEY,
  CardName           TEXT    NOT NULL,
  ManaCost           TEXT,              -- e.g. "{2}{G}{G}"
  ConvertedManaCost  REAL,              -- numeric
  Abilities          TEXT,              -- newline-separated or JSON
  FlavorText         TEXT,
  Power              TEXT,              -- some cards have '*' etc.
  Toughness          TEXT,
  ImageURL           TEXT,
  Layout             TEXT,              -- 'normal', 'split', 'flip', 'transform', etc.
  SuperType          TEXT,              -- 'Legendary', 'Basic', 'Snow', etc.
  ArtistID           INTEGER NOT NULL,
  RarityID           INTEGER NOT NULL,
  SetID              INTEGER NOT NULL,
  FOREIGN KEY (ArtistID) REFERENCES Artist(ArtistID),
  FOREIGN KEY (RarityID) REFERENCES Rarity(RarityID),
  FOREIGN KEY (SetID)    REFERENCES CardSet(SetID)
);

-- Junction: Card ↔ Color (many-to-many)
CREATE TABLE IF NOT EXISTS Card_Color (
  CardID  INTEGER NOT NULL,
  ColorID INTEGER NOT NULL,
  PRIMARY KEY (CardID, ColorID),
  FOREIGN KEY (CardID)  REFERENCES Card(CardID)  ON DELETE CASCADE,
  FOREIGN KEY (ColorID) REFERENCES Color(ColorID) ON DELETE CASCADE
);

-- Junction: Card ↔ CardType (many-to-many)
CREATE TABLE IF NOT EXISTS Card_CardType (
  CardID     INTEGER NOT NULL,
  CardTypeID INTEGER NOT NULL,
  PRIMARY KEY (CardID, CardTypeID),
  FOREIGN KEY (CardID)     REFERENCES Card(CardID)     ON DELETE CASCADE,
  FOREIGN KEY (CardTypeID) REFERENCES CardType(CardTypeID) ON DELETE CASCADE
);

-- Junction: Card ↔ SubType (many-to-many)
CREATE TABLE IF NOT EXISTS Card_SubType (
  CardID    INTEGER NOT NULL,
  SubTypeID INTEGER NOT NULL,
  PRIMARY KEY (CardID, SubTypeID),
  FOREIGN KEY (CardID)    REFERENCES Card(CardID)    ON DELETE CASCADE,
  FOREIGN KEY (SubTypeID) REFERENCES SubType(SubTypeID) ON DELETE CASCADE
);