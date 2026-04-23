'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import type { StateInfo } from '@/lib/listings'

export default function SearchBar({ states }: { states: StateInfo[] }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const filtered = query.length > 0
    ? states.filter(s => s.name.toLowerCase().includes(query.toLowerCase()))
    : states

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  return (
    <div ref={ref} className="relative w-full max-w-md">
      <label htmlFor="state-search" className="sr-only">Search by state</label>
      <input
        id="state-search"
        type="text"
        value={query}
        onChange={e => { setQuery(e.target.value); setOpen(true) }}
        onFocus={() => setOpen(true)}
        placeholder="Enter your state…"
        autoComplete="off"
        className="w-full px-5 py-4 text-lg rounded-xl border-2 border-white/40 bg-white text-gray-900 placeholder-gray-400 shadow-lg focus:outline-none focus:border-primary-600"
        aria-label="Search by state"
        aria-expanded={open}
        aria-controls="state-listbox"
        aria-haspopup="listbox"
        role="combobox"
        aria-autocomplete="list"
      />
      {open && filtered.length > 0 && (
        <ul
          id="state-listbox"
          role="listbox"
          aria-label="States"
          className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-xl z-20 max-h-56 overflow-y-auto"
        >
          {filtered.map(s => (
            <li key={s.slug} role="option" aria-selected={false}>
              <Link
                href={`/${s.slug}`}
                onClick={() => setOpen(false)}
                className="flex justify-between items-center px-5 py-3 hover:bg-primary-50 text-gray-800 transition-colors"
              >
                <span className="font-medium">{s.name}</span>
                <span className="text-sm text-gray-400">{s.count} contractors</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
