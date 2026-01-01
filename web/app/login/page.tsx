import { redirect } from 'next/navigation'

type SearchParams = Record<string, string | string[] | undefined>

const toSearchString = (searchParams: SearchParams) => {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(searchParams)) {
    if (typeof value === 'string')
      params.set(key, value)
    else if (Array.isArray(value))
      value.forEach(v => params.append(key, v))
  }
  const text = params.toString()
  return text ? `?${text}` : ''
}

const Login = ({ searchParams }: { searchParams?: SearchParams }) => {
  redirect(`/signin${toSearchString(searchParams || {})}`)
}

export default Login
