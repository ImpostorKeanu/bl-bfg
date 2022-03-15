
# Client ID Source: https://github.com/Gerenios/AADInternals/blob/master/AccessToken_utils.ps1#L11
# Parsed Structure: {client:{tag:ID}}

COMMON_CLIENT_IDS = CIDS = \
{'aad_account': {'https://account.activedirectory.windowsazure.com': ['0000000c-0000-0000-c000-000000000000']},
 'aadconnectv2': {'AADConnectv2': ['6eb59a73-39b2-4c23-a70f-e2e3ce8965b1']},
 'aadrm': {'AADRM': ['90f610bf-206d-4950-b61d-37fa6fd1b224']},
 'aadsync': {'AzureADSync': ['cb1056e2-e479-49de-ae31-7812af012ed8']},
 'az': {'AADJCSP': ['b90d5b8f-5503-4153-b545-b31cecfaece2'],
        'AADPinredemptionclient': ['06c6433f-4fb8-4670-b2cd-408938296b8e'],
        'AZPowerShellModule': ['1950a258-227b-4e31-a9cf-717495945fc2'],
        'AppleInternetAccounts': ['f8d98a96-0999-43f5-8af3-69971c7bb423'],
        'AuthenticatorAppresource:ff9ebd75-fe62-434a-a6ce-b3f0a8592eaf': ['4813382a-8fa7-425e-ab75-3b753aab3abb'],
        'AzureAndroidApp': ['0c1307d4-29d6-4389-a11c-5cbe7f65d7fa'],
        'IntuneMAMclientresource:https://intunemam.microsoftonline.com': ['6c7e8096-f593-4d72-807f-a5f86dcc9c77'],
        'Microsoft.AAD.BrokerPluginresource:https://cs.dds.microsoft.com': ['6f7e0f60-9401-4f5b-98e2-cf15bd5fd5e3'],
        'MicrosoftAADCloudAP': ['38aa3b87-a06d-4817-b275-7a316988d93b'],
        'MicrosoftAuthenticationBroker(AzureMDMclient)': ['29d9ed98-a469-4536-ade2-f981bc1d605e'],
        'MicrosoftExchangeRESTAPIBasedPowershell': ['fb78d390-0c51-40cd-8e17-fdbfab77341b'],
        'Microsoft_AAD_RegisteredApps': ['18ed3507-a475-4ccb-b669-d66bc9f2a36e'],
        'Office365Management(mobileapp)': ['00b41c95-dab0-4487-9791-b9d2c32c80f2'],
        'SPOManagementShell': ['9bc3ab49-b65d-410a-85ad-de819febfddc'],
        'Teamsclient': ['1fec8e78-bce4-4aaf-ab1b-5451cc387264'],
        'WindowsConfigurationDesigner(WCD)': ['de0853a1-ab20-47bd-990b-71ad5077ac7b'],
        'code-try-0': ['7f59a773-2eaf-429c-a059-50fc5bb28b44'],
        'https://mysignins.microsoft.com': ['19db86c3-b2b9-44cc-b339-36da233a3be2']},
 'azure_mgmt': {'WindowsAzureServiceManagementAPI': ['84070985-06ea-473d-82fe-eb82b4011c9d']},
 'azureadmin': {'AzureAdminwebui': ['c44b4083-3bb0-49c1-b47d-974e53cbdf3c']},
 'azuregraphclientint': {'MicrosoftAzureGraphClientLibrary2.1.9Internal': ['7492bca1-9461-4d94-8eb8-c17896c61205']},
 'dynamicscrm': {'DynamicsCRM': ['00000007-0000-0000-c000-000000000000']},
 'exo': {'EXORemotePowerShell': ['a0c73c16-a7e3-4564-9a95-2bdf47383716']},
 'graph_api': {'MSGraphAPI': ['1b730954-1685-4b74-9bfd-dac224a7b894']},
 'msmamservice': {'MSMAMServiceAPI': ['27922004-5251-4030-b22d-91ecd9a37ea4']},
 'o365exo': {'ExchangeOnline': ['00000002-0000-0ff1-ce00-000000000000']},
 'o365spo': {'SharePointOnline': ['00000003-0000-0ff1-ce00-000000000000']},
 'o365suiteux': {'O365SuiteUX': ['4345a7b9-9a63-4910-a426-35363201d503']},
 'office': {'Office,ref.https://docs.microsoft.com/en-us/office/dev/add-ins/develop/register-sso-add-in-aad-v2': ['d3590ed6-52b3-4102-aeff-aad2292ab01c']},
 'office_mgmt': {'OfficeManagementAPIEditorhttps://manage.office.com': ['389b1b32-b5d5-43b2-bddc-84ce938d6737']},
 'office_online': {'OutlookOnlineAdd-inApp': ['bc59ab01-8403-45c6-8796-ac3ef710b3e3']},
 'office_online2': {'SharePointOnlineClient': ['57fb890c-0dab-4253-a5e0-7188c88b2bb4']},
 'onedrive': {'OneDriveSyncEngine': ['ab9b8c07-8f02-4f72-87fa-80105867a763']},
 'patnerdashboard': {'Partnerdashboard(missingonletter?)': ['4990cffe-04e8-4e8b-808a-1175604b879']},
 'powerbi_contentpack': {'PowerBIcontentpack': ['2a0c3efa-ba54-4e55-bdc0-770f9e39e9ee']},
 'pta': {'Pass-throughauthentication': ['cb1056e2-e479-49de-ae31-7812af012ed8']},
 'sara': {'MicrosoftSupportandRecoveryAssistant(SARA)': ['d3590ed6-52b3-4102-aeff-aad2292ab01c']},
 'skype': {'Skype': ['d924a533-3729-4708-b3e8-1d2445af35e3']},
 'synccli': {'Syncclient': ['1651564e-7ce4-4d99-88be-0a65050d8dc3']},
 'teams': {'Teams': ['1fec8e78-bce4-4aaf-ab1b-5451cc387264']},
 'teamswebclient': {'Teamswebclient': ['5e3ce6c0-2b1f-4285-8d4b-75ee78787346']},
 'webshellsuite': {'Office365ShellWCSS-Client': ['89bee1f7-5e6e-4d8a-9f3d-ecd601259da7']},
 'www': {'Officeportal': ['00000006-0000-0ff1-ce00-000000000000']}}

RESOURCES = \
{'aad_graph_api': 'https://graph.windows.net',
 'ms_graph_api': 'https://graph.microsoft.com',
 'azure_mgmt_api': 'https://management.azure.com',
 'windows_net_mgmt_api': 'https://management.core.windows.net/',
 'cloudwebappproxy': 'https://proxy.cloudwebappproxy.net/registerapp',
 'officeapps': 'https://officeapps.live.com',
 'outlook': 'https://outlook.office365.com',
 'webshellsuite': 'https://webshell.suite.office.com',
 'sara': 'https://api.diagnostics.office.com',
 'office_mgmt': 'https://manage.office.com',
 'msmamservice': 'https://msmamservice.api.application',
 'spacesapi': 'https://api.spaces.skype.com'}

# ==============================================
# CLIENT IDS KNOWN TO WORK WITH ANY RESOURCE URL
# ==============================================

MSOL_UNIVERSAL_CLIENT_IDS = \
['1b730954-1685-4b74-9bfd-dac224a7b894', 
  '90f610bf-206d-4950-b61d-37fa6fd1b224',
  'a0c73c16-a7e3-4564-9a95-2bdf47383716',
  'd924a533-3729-4708-b3e8-1d2445af35e3',
  '00000006-0000-0ff1-ce00-000000000000',
  '00000003-0000-0ff1-ce00-000000000000',
  '00000002-0000-0ff1-ce00-000000000000',
  '00000007-0000-0000-c000-000000000000',
  '4345a7b9-9a63-4910-a426-35363201d503',
  'cb1056e2-e479-49de-ae31-7812af012ed8',
  'c44b4083-3bb0-49c1-b47d-974e53cbdf3c',
  'cb1056e2-e479-49de-ae31-7812af012ed8',
  '89bee1f7-5e6e-4d8a-9f3d-ecd601259da7',
  '1fec8e78-bce4-4aaf-ab1b-5451cc387264',
  'd3590ed6-52b3-4102-aeff-aad2292ab01c',
  '57fb890c-0dab-4253-a5e0-7188c88b2bb4',
  'bc59ab01-8403-45c6-8796-ac3ef710b3e3',
  '2a0c3efa-ba54-4e55-bdc0-770f9e39e9ee',
  '0000000c-0000-0000-c000-000000000000',
  'd3590ed6-52b3-4102-aeff-aad2292ab01c',
  '389b1b32-b5d5-43b2-bddc-84ce938d6737',
  'ab9b8c07-8f02-4f72-87fa-80105867a763',
  '27922004-5251-4030-b22d-91ecd9a37ea4',
  '5e3ce6c0-2b1f-4285-8d4b-75ee78787346',
  '1950a258-227b-4e31-a9cf-717495945fc2',
  'f8d98a96-0999-43f5-8af3-69971c7bb423',
  '7f59a773-2eaf-429c-a059-50fc5bb28b44',
  '9bc3ab49-b65d-410a-85ad-de819febfddc',
  '19db86c3-b2b9-44cc-b339-36da233a3be2',
  '00b41c95-dab0-4487-9791-b9d2c32c80f2',
  '29d9ed98-a469-4536-ade2-f981bc1d605e',
  '6f7e0f60-9401-4f5b-98e2-cf15bd5fd5e3',
  '0c1307d4-29d6-4389-a11c-5cbe7f65d7fa',
  '6c7e8096-f593-4d72-807f-a5f86dcc9c77',
  '4813382a-8fa7-425e-ab75-3b753aab3abb',
  '1fec8e78-bce4-4aaf-ab1b-5451cc387264',
  'de0853a1-ab20-47bd-990b-71ad5077ac7b',
  'b90d5b8f-5503-4153-b545-b31cecfaece2',
  'fb78d390-0c51-40cd-8e17-fdbfab77341b',
  '18ed3507-a475-4ccb-b669-d66bc9f2a36e']
