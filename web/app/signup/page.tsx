'use client'
import { useRouter, useSearchParams } from 'next/navigation'
import { useCallback, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { API_PREFIX } from '@/config'
import MailForm from './components/input-mail'

const Signup = () => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { t } = useTranslation()
  const noAceDataCloudOAuth = searchParams.get('no_acedatacloud_oauth') === '1'

  useEffect(() => {
    if (noAceDataCloudOAuth)
      return
    if (typeof window === 'undefined')
      return
    const loginUrl = new URL(`${API_PREFIX}/oauth/login/acedatacloud`, window.location.origin)
    if (window.location.search)
      loginUrl.search = new URLSearchParams(window.location.search).toString()
    window.location.href = loginUrl.toString()
  }, [noAceDataCloudOAuth])

  const handleInputMailSubmitted = useCallback((email: string, result: string) => {
    const params = new URLSearchParams(searchParams)
    params.set('token', encodeURIComponent(result))
    params.set('email', encodeURIComponent(email))
    router.push(`/signup/check-code?${params.toString()}`)
  }, [router, searchParams])

  return (
    <div className="mx-auto mt-8 w-full">
      <div className="mx-auto mb-10 w-full">
        <h2 className="title-4xl-semi-bold text-text-primary">{t('signup.createAccount', { ns: 'login' })}</h2>
        <p className="body-md-regular mt-2 text-text-tertiary">{t('signup.welcome', { ns: 'login' })}</p>
      </div>
      <MailForm onSuccess={handleInputMailSubmitted} />
    </div>
  )
}

export default Signup
