from dataclasses import dataclass, field, astuple

@dataclass(frozen=True, order=True, init=False)
class Quote:
    quoteid: int | None = field(repr=False)
    name: str
    year: str
    quote: str
    numlikes: int = 0
    
    def __init__(self, quoteid, name, year, quote=None, numlikes=0) -> None:
        """creates the quote dataclass. NOTE: this is set-up so that if quoteid is a string it will assume that there is none
           and set name=quoteid, year=name etc. this is for compatibility with database
        """
        if isinstance(quoteid, str):
            object.__setattr__(self, "quoteid", None)
            object.__setattr__(self, "name", quoteid)
            object.__setattr__(self, "year", name)
            object.__setattr__(self, "quote", year)
            if quote is None:
                object.__setattr__(self, "numlikes", 0)
            object.__setattr__(self, "numlikes", quote)
            return
        object.__setattr__(self, "quoteid", quoteid)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "year", year)
        object.__setattr__(self, "quote", quote)
        object.__setattr__(self, "numlikes", numlikes)
    
    def __iter__(self):
        for x in astuple(self):
            if x is not None:
                yield x
                