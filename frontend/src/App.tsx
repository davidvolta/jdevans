import { useState, useEffect } from 'react'
import { BrowserRouter } from 'react-router-dom'
import MobileLayout from './MobileLayout'
import DesktopLayout from './DesktopLayout'
import type { Poem } from './PoemList'
import './App.css'

// Sample poem data for testing the design
const samplePoems: (Poem & { body: string })[] = [
  {
    id: '1',
    title: 'It was future shock (chimpanzee-style)',
    body: `News item: Ham, the first chimpanzee to ride a
rocket into space, has died at the age of 26. Ham
rode a Redstone rocket into a sub-orbital flight on
Jan. 3l, l96l. He died at a North Carolina zoological
park where he had lived for 2 1/2 years.

He was never the same when he came back from space.
He seemed awkward. Uneasy. Alone. Out of place.
He'd sit in his cage with a strange, dreamy stare,
a smug sort of look for a "dumb" chimp to wear.

He wouldn't play games with his simian brothers
("Hide Your Ears" "Chase Your Tail" and all of the others.)
He would sit there for hours, alone and content,
gazing endlessly out at the vast firmament.

His trip to the ozone had changed Ham inside.
It was more than a journey, much more than a ride.
He had seen the earth curve, seen mountains and seas,
he had swung toward the sun on a cosmic trapeze.

From the earth to the stars in a single lifetime,
while thousands of species still crawled through the slime.
Darwin was right; Ham became a believer.
Zoologically speaking, he was an overachiever.

He never fit in when he came back to earth.
His brief rocket flight was a strange second birth.
Trapped on a ladder between monkey and man:
A small step for NASA, a big leap for Ham.

The kids who stopped by to see Ham at the zoo
weren't really impressed, but then they never knew
all the dizzying thoughts that would race through his brain.
Poor Ham just sat there. He couldn't explain.

I like to think that the zoo's personnel
who were sent in to clean out poor Ham's little cell
swept out so quickly they just didn't see
Ham's scrawl in the dust: E=MC ...`,
  },
  {
    id: '2',
    title: 'Harbingers of spring: Nature\'s page one story',
    body: `A leafy "thing" erupted in my front yard overnight.
A crocus maybe. (I can't tell.) But what a longed-for sight.
The earth is still a-ticking to a rhythm all its own:
the constant and determined beat of Nature's metronome.
It hasn't paused a "tick" for you, nor held a "tock" for me;
it hasn't been distracted from its endless symphony.
It doesn't care if Beirut falls or if a premier dies.
What mankind finds "important" it has yet to recognize.
My morning paper missed the news. It wasn't on Page 1.
It glimmered green and silent in the brilliant morning sun.
A banner headline might have said: Spring? Early Overtures.
The story needed just one line: "The universe endures."`,
  },
  {
    id: '3',
    title: 'Clipping coupons: unkindest of cuts?',
    body: `Rise up, you coupon clippers!
Let's end the coupon game
that keeps us all a-clipping
for discounts we can claim.

The corporate gnomes all giggle
as they watch us cut and clip,
collecting cents-off coupons
for our weekly shopping trip.

"A nickle off on Bounty!"
"A quarter off on Tide!"
We clip, and clip and clip them
and we set them all aside.

We hoard them all like misers.
Our thrift turns into greed.
We start collecting coupons
good for products we don't need!

We slash the daily papers,
we shred our magazines,
hunting coupons, coupons, coupons,
with a passion rarely seen.

On shopping day it's combat.
We storm the grocery aisles
snatching product-coupon "matches"
like consumer crocodiles.

And is our effort worth it?
Is our thriftiness admired?
"I'm sorry, sir," the cashier whines,
"this coupon has expired."`,
  },
  {
    id: '4',
    title: 'Twinkle, twinkle liflle star, \'Mr. C\' knows why you are',
    body: `News item: STOCKHOLM, Sweden - The Royal
Swedish Academy of Sciences announced Wednesday
that professor Subrahmanyan Chandrasekhar of the
University of Chicago won a Nobel Prize in physics
for his work on the evolution of stars.

Subrahmanyan Chandrasekhar
has cause to thank his lucky star.
It brought him glory, brought him fame,
for theories complex as his name.
Thanks to Mr. Chandrasekhar
we need not wonder what stars are.
But even brilliant Mr. C.
cannot resolve one mystery:
Can they print a name that size
on one small, golden, Nobel prize?`,
  },
  {
    id: '5',
    title: 'No news is front-page stuff for the supermarket tabloids',
    body: `Did Pope John Paul see UFOs?
Do Brussels sprouts cure cancer?
Did one of Santa's reindeer die?
(Was it Comet? Rudolph? Prancer?)
Can you lose 20 pounds a day
by eating only prunes?
Did Ron and Nancy really go
on separate honeymoons?
Was Jackie O. a prisoner
on Walter Cronkite's yacht?
Can you improve your memory
by munching apricots?
Is Frank Sinatra penniless?
Is Brezhnev really dead?
Can children boost their IQ scores
by eating raisin bread?
Is Princess Di a Russian spy?
Is Henny Youngman Catholic?
Does Cathy Crosby talk to Bing?
Is Bob Hope telepathic?

I made up all those questions,
but who knows? They could be true.
Would anyone believe it, though?
Gee. I don't know.Would you?`,
  }
]

function useIsMobile() {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)
  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])
  return isMobile
}

function App() {
  const [poems, setPoems] = useState<(Poem & { body: string })[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const isMobile = useIsMobile()

  useEffect(() => {
    fetch('http://localhost:8000/poems')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch poems')
        return res.json()
      })
      .then(data => {
        setPoems(data.poems)
        setIsLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setIsLoading(false)
      })
  }, [])

  if (isLoading) {
    return (
      <div className="loading">
        <img src="/loader.gif" alt="Loading..." className="loading-gif" />
        <span>Loading poems...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="loading error">
        <span>Error: {error}</span>
      </div>
    )
  }

  return (
    <BrowserRouter>
      {isMobile ? <MobileLayout poems={poems} /> : <DesktopLayout poems={poems} />}
    </BrowserRouter>
  )
}

export default App
