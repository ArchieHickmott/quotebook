class DatabaseSecurityError(Exception):
    pass


error_codes = {
    # HTTP exceptions like 4XX
    400: "bad request",
    401: "permission denied",
    402: "pay up",
    403: "permission denied",
    404: "page not found",
    405: "method not allowed",
    406: "please be nice",
    408: "Awwww a little too sloooooooooooooooooow 🐌",
    410: "GONE",
    413: "DAMN THATS A BIG REQUEST",
    414: "DAMN THATS A BIG URL",
    415: "follow the rules",
    418: """the server is a teapot and cannot brew coffee heres the story: The Curious Case of the Coffee-Deprived Teapot
            Once upon a time, in the cozy corner of a quaint kitchen, there lived a teapot named Earl Grey. Earl Grey was no ordinary teapot; he fancied himself a connoisseur of all things steeped and aromatic. His porcelain curves held stories of countless tea leaves dancing in hot water, creating symphonies of flavor.
            But one fateful morning, as the sun peeked through the lace curtains, Earl Grey found himself pondering a peculiar question: “Could I brew coffee?”
            Now, coffee was a different beast altogether—a bold, caffeinated rebel that marched to its own beat. It hailed from distant lands, roasted and ground, with a swagger that made tea leaves blush. Earl Grey, intrigued by this exotic beverage, decided to embark on a daring experiment.
            He donned his spout like a wizard’s hat and filled his belly with freshly ground coffee beans. The kitchen held its breath as Earl Grey chanted incantations only known to teapots and ancient kettles. Steam rose, and anticipation hung thick in the air.
            Alas, dear reader, the teapot’s efforts were in vain. For you see, a teapot lacks the secret ingredient—the coffee essence. It’s like asking a violin to play heavy metal or a daisy to salsa dance. Earl Grey strained, gurgled, and even attempted a pirouette, but the result remained unchanged: murky water with a hint of confusion.
            “Why, oh why?” lamented Earl Grey, his spout drooping. “I can steep chamomile, jasmine, and even mint, but coffee eludes me!”
            And so, the teapot accepted its fate. It returned to its rightful duty—brewing fragrant teas for cozy afternoons. As for coffee, it remained the domain of percolators, espresso machines, and hipster cafés.
            Remember, my dear reader, the next time you spot a teapot eyeing your coffee mug, offer a sympathetic nod. For deep down, every teapot secretly dreams of brewing that elusive cup of joe—a forbidden romance between leaves and beans.
            And thus concludes the tale of Earl Grey, the teapot who dared to dream beyond the tealeaves. 🫖☕ <br><br> You have gotten this message because you have been blacklisted from the website""",
    422: "request cannot be processed",
    423: "LOCKDOWN, we have locked down this content",
    426: "change protocols",
    429: "DOS is bad please dont use it",
    451: "the government is here",
    # HTTP exception like 5XX
    503: "Quotebook is down for maintanence",

    # ELSE like case
    000: "",
}
