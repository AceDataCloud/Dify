'use client'
import type { App } from '@/models/explore'
import type { TryAppSelection } from '@/types/try-app'
import { PlusIcon } from '@heroicons/react/20/solid'
import { RiInformation2Line } from '@remixicon/react'
import { useTranslation } from 'react-i18next'
import AppIcon from '@/app/components/base/app-icon'
import { useGlobalPublicStore } from '@/context/global-public-context'
import { AppModeEnum } from '@/types/app'
import { cn } from '@/utils/classnames'
import { AppTypeIcon } from '../../app/type-selector'
import Button from '../../base/button'

export type AppCardProps = {
  app: App
  canCreate: boolean
  onCreate: () => void
  onTry: (params: TryAppSelection) => void
  isExplore?: boolean
}

const AppCard = ({
  app,
  canCreate,
  onCreate,
  onTry,
  isExplore = true,
}: AppCardProps) => {
  const { t } = useTranslation()
  const { app: appBasicInfo } = app
  const { systemFeatures } = useGlobalPublicStore()
  const isTrialApp = app.can_trial && systemFeatures.enable_trial_app
  const isAceDataCloud = app.source === 'acedatacloud'
  const handleTryApp = () => {
    onTry({ appId: app.app_id, app })
  }

  return (
    <div className={cn(
      'group relative col-span-1 flex cursor-pointer flex-col overflow-hidden rounded-lg border-[0.5px] bg-components-panel-on-panel-item-bg pb-2 shadow-sm transition-all duration-200 ease-in-out hover:bg-components-panel-on-panel-item-bg-hover hover:shadow-lg',
      isAceDataCloud
        ? 'border-util-colors-blue-blue-200 ring-1 ring-util-colors-blue-blue-100'
        : 'border-components-panel-border',
    )}>
      {isAceDataCloud && (
        <div className="absolute right-0 top-0 rounded-bl-lg bg-util-colors-blue-blue-50 px-2 py-0.5">
          <span className="text-[10px] font-medium leading-[14px] text-util-colors-blue-blue-600">
            Ace Data Cloud
          </span>
        </div>
      )}
      <div className="flex h-[66px] shrink-0 grow-0 items-center gap-3 px-[14px] pb-3 pt-[14px]">
        <div className="relative shrink-0">
          <AppIcon
            size="large"
            iconType={appBasicInfo.icon_type}
            icon={appBasicInfo.icon}
            background={appBasicInfo.icon_background}
            imageUrl={appBasicInfo.icon_url}
          />
          <AppTypeIcon
            wrapperClassName="absolute -bottom-0.5 -right-0.5 w-4 h-4 shadow-sm"
            className="h-3 w-3"
            type={appBasicInfo.mode}
          />
        </div>
        <div className="w-0 grow py-[1px]">
          <div className="flex items-center text-sm font-semibold leading-5 text-text-secondary">
            <div className="truncate" title={appBasicInfo.name}>{appBasicInfo.name}</div>
          </div>
          <div className="flex items-center text-[10px] font-medium leading-[18px] text-text-tertiary">
            {appBasicInfo.mode === AppModeEnum.ADVANCED_CHAT && <div className="truncate">{t('types.advanced', { ns: 'app' }).toUpperCase()}</div>}
            {appBasicInfo.mode === AppModeEnum.CHAT && <div className="truncate">{t('types.chatbot', { ns: 'app' }).toUpperCase()}</div>}
            {appBasicInfo.mode === AppModeEnum.AGENT_CHAT && <div className="truncate">{t('types.agent', { ns: 'app' }).toUpperCase()}</div>}
            {appBasicInfo.mode === AppModeEnum.WORKFLOW && <div className="truncate">{t('types.workflow', { ns: 'app' }).toUpperCase()}</div>}
            {appBasicInfo.mode === AppModeEnum.COMPLETION && <div className="truncate">{t('types.completion', { ns: 'app' }).toUpperCase()}</div>}
          </div>
        </div>
      </div>
      <div className="description-wrapper h-[90px] px-[14px] text-text-tertiary system-xs-regular">
        <div className="line-clamp-4 group-hover:line-clamp-2">
          {app.description}
        </div>
      </div>
      {isExplore && (canCreate || isTrialApp) && (
        <div className={cn('absolute bottom-0 left-0 right-0 hidden bg-gradient-to-t from-components-panel-gradient-2 from-[60.27%] to-transparent p-4 pt-8 group-hover:flex')}>
          <div className={cn('grid h-8 w-full grid-cols-1 space-x-2', canCreate && 'grid-cols-2')}>
            {
              canCreate && (
                <Button variant="primary" className="h-7" onClick={() => onCreate()}>
                  <PlusIcon className="mr-1 h-4 w-4" />
                  <span className="text-xs">{t('appCard.addToWorkspace', { ns: 'explore' })}</span>
                </Button>
              )
            }
            <Button className="h-7" onClick={handleTryApp}>
              <RiInformation2Line className="mr-1 size-4" />
              <span>{t('appCard.try', { ns: 'explore' })}</span>
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default AppCard
