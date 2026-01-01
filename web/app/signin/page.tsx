import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import SignInClient from './signin-client'

type SearchParams = Record<string, string | string[] | undefined>
type CookieStore = Awaited<ReturnType<typeof cookies>>

const first = (value: string | string[] | undefined) => Array.isArray(value) ? value[0] : value

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

const shouldAutoRedirectToAceDataCloudOAuth = (cookieStore: CookieStore, searchParams: SearchParams) => {
  if (cookieStore.get('access_token')?.value)
    return false
  if (first(searchParams.message))
    return false
  if (first(searchParams.step) === 'next')
    return false
  if (first(searchParams.no_acedatacloud_oauth) === '1')
    return false
  return true
}

const SignIn = async ({ searchParams }: { searchParams?: SearchParams }) => {
  const safeSearchParams = searchParams || {}
  const cookieStore = await cookies()
  if (shouldAutoRedirectToAceDataCloudOAuth(cookieStore, safeSearchParams)) {
    const query = toSearchString(safeSearchParams)
    redirect(`/console/api/oauth/login/acedatacloud${query}`)
  }
  return <SignInClient />
}

export default SignIn
