from sqlalchemy import (Table, 
                        Column,
                        Integer,
                        String,
                        MetaData,
                        TIME,
                        Boolean,
                        ForeignKey
)


metadata = MetaData()

quotes = Table(
    "quotes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("content", String),
    Column("author", String),
    Column("year", TIME)
)

logs = Table(
    "logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("route", String),
    Column("parameters", String),
    Column("time", TIME),
    Column("ip", String),
    Column("quoteid", ForeignKey("quotes.id"))
)

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("add", Boolean),
    Column("edit", Boolean),
    Column("delete", Boolean),
)
