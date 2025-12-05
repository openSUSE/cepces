# Windows Server setup for Certificate Auto Enrollment

**Prerequisites:** You need an Active Directory Domain Controller (AD DC) and
a Certificate Authority (CA) Domain Member (Windows Server 2025).

## On the enrolled AD DC

### Create a user for the CEP/CES service

Create a domain user account to act as the service account for the Certificate
Enrollment Web Service. See Microsoft's documentation on [creating a domain
user account for the service][service-account].

[service-account]: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/configure-certificate-enrollment-web-service#create-a-domain-user-account-to-act-as-the-service-account

```
$addc = Get-ADDomainController
$realm = $addc.domain.ToUpper()
$dnsdomain = $addc.domain
$domain = $realm.split('\.')[0]
$hostname = $addc.hostname

$ces_username = "cepcessvc"
$ces_username_lower = $ces_username.toLower()
$ces_upn = "$ces_username_lower@$dnsdomain"
$ces_domuser = "$domain\$ces_username"
$ces_secpasswd = ConvertTo-SecureString -String "P@sSwOrd1" -AsPlainText -Force

New-ADUser -Name $ces_username -GivenName $ces_username -Surname Service -DisplayName "CES Service" -UserPrincipalName $ces_upn -AccountPassword $ces_secpasswd -ChangePasswordAtLogon:$false -PasswordNeverExpires $true -Enabled $true
```

Set the Service Principal Name (SPN) for the host running the CA. See
Microsoft's documentation on [setting a service principal name for the service
account][set-spn] for more details.

[set-spn]: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/configure-certificate-enrollment-web-service#set-a-service-principal-name-for-the-service-account

```
$ca_hostname = "<REPLACE ME>"
$ca_fqdn = "$ca_hostname.$dnsdomain"
setspn -s http/$ca_hostname $ces_username
setspn -s http/$ca_fqdn $ces_username
```

### Configure the Certificate Enrollment Web Service user account for constrained delegation (AD DC)

Configure constrained delegation to allow the service account to authenticate
on behalf of users. See Microsoft's documentation on [configuring the
Certificate Enrollment Web Service user account for constrained
delegation][constrained-delegation] for more details.

[constrained-delegation]: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/configure-certificate-enrollment-web-service#configure-the-certificate-enrollment-web-service-user-account-for-constrained-delegation

```
Get-ADUser -Identity $ces_username | Set-ADAccountControl -TrustedToAuthForDelegation $True
Set-ADUser -Identity $ces_username -Add @{"msDS-AllowedToDelegateTo"=@("HOST/$ca_fqdn", "rpcss/$ca_fqdn")}
```

## On the CA Server (Domain Member)

### Install Certificate Service Windows Features

```
Install-WindowsFeature -Name "RSAT-AD-PowerShell" –IncludeAllSubFeature
Add-WindowsFeature -Name @('ADCS-Enroll-Web-Pol','ADCS-Enroll-Web-Svc','ADCS-Web-Enrollment') -IncludeManagementTools
```

### Add CES domain user to the local IIS_IUSRS group

Add the service account to the local IIS_IUSRS group to grant necessary
permissions for IIS. See Microsoft's documentation on [adding the service
account to the local IIS_IUSERS group][add-iis-users] for more details.

[add-iis-users]: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/configure-certificate-enrollment-web-service#add-the-service-account-to-the-local-iis_iusers-group

```
$addom = Get-ADDomain -Current LocalComputer
$realm = $addom.forest.ToUpper()
$dnsdomain = $addom.dnsroot
$domain = $addom.NetBIOSName

$ces_username = "cepcessvc"
$ces_domuser = "$domain\$ces_username"
$ces_secpasswd = ConvertTo-SecureString -String "P@sSwOrd1" -AsPlainText -Force

net localgroup IIS_IUSRS $ces_username /Add
net localgroup IIS_IUSRS
```

### Setup the Certificate Authority

```
$admin_creds = Get-Credential $domain\Administrator

$params = @{
    CAType                  = "EnterpriseRootCA"
    CACommonName            = "$domain-ROOT-CA"
    CryptoProviderName      = "RSA#Microsoft Software Key Storage Provider"
    KeyLength               = 4096
    HashAlgorithmName       = "SHA512"
    OverwriteExistingCAinDS = $true
    OverwriteExistingKey    = $true
    Credential              = $admin_creds
    Force                   = $true
}
Add-WindowsFeature -Name @('ADCS-Cert-Authority') -IncludeManagementTools
Install-AdcsCertificationAuthority @params
```

### The CES service account needs have read permission on the CA

**These are manual steps:**

1. Open the "Certification Authority" Console
2. Right Click on the CA -> Properties
3. On the Security tab click on "Add .."
4. Add the CEP/CES service account (cepcessvc).
5. For the CES account ensure that the "Allow" check box is selected
   for "Read". Clear the "Allow" check box for "Request Certificates"

## Request a Server Certificate for the Webserver from CA

Request and configure an SSL/TLS certificate for the IIS web server using the
Enterprise CA. This is required for secure HTTPS communication with the
Certificate Enrollment services. See the archived TechNet Wiki guide on
[configuring SSL/TLS on a web site in the domain with an Enterprise
CA][ssl-config] for detailed step-by-step instructions.

[ssl-config]: https://learn.microsoft.com/en-us/archive/technet-wiki/12485.configure-ssltls-on-a-web-site-in-the-domain-with-an-enterprise-ca

## Restart IIS service

```
iisreset /restart
```

### Configure the Certificate Enrollment Policy Web Service

#### Get the SSL Certificate Thumbprint of the Web Server

Retrieve the SSL certificate thumbprint needed for configuring the enrollment
services. See Microsoft's documentation on [selecting a server
certificate][select-cert] for more details.

[select-cert]: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/configure-certificate-enrollment-web-service#select-a-server-certificate

```
Import-Module WebAdministration
$certs = Get-ChildItem IIS:SSLBindings | Foreach-Object {
  [PSCustomObject]@{
     Site=$_.sites.value
     HostName=$_.Host
     Port=$_.Port
     Thumb=$_.thumbprint
  }
}
```

If there are more than 2 certificates, use the Thumb linked with Port 443 in
`$certs`. Use it as `SSLCertThumbprint` in the next step.

```
$params = @{
    AuthenticationType     = "Kerberos"
    SSLCertThumbprint      = $certs.thumb
    Credential             = $admin_creds
}
Install-AdcsEnrollmentPolicyWebService @params -Force
```

### Configure the Certificate Enrollment Web service

This is using the CEP/CEP service account we created:

```
$caconfig_tmp = certutil | findstr "Config"
$caconfig = $caconfig_tmp.split('"')[1]

$params = @{
    CAConfig               = $caconfig
    AuthenticationType     = "Kerberos"
    SSLCertThumbprint      = $certs.thumb
    ServiceAccountName     = $ces_domuser
    ServiceAccountPassword = $ces_secpasswd
    Credential             = $admin_creds
}
Install-AdcsEnrollmentWebService @params -Force
```

### Configure the Certification Authority Web Enrollment

```
Install-AdcsWebEnrollment -Credential $admin_creds -Force
```

## On the Active Directory domain controller

### Set GPO for Auto Enrollment

If you run:

```
Get-CertificateAutoEnrollmentPolicy -Scope Applied -context Machine
```

by default you should see:

```
PolicyState                : NotConfigured
EnableMyStoreManagement    : False
EnableTemplateCheck        : False
ExpirationPercentage       : 0
StoreName                  :
EnableBalloonNotifications : False
```

### Set AutoEnrollment

```
Set-GPRegistryValue -Name "Default Domain Policy" -Key "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Cryptography\AutoEnrollment" -ValueName "AEPolicy" -Value 7 -Type "Dword"

Set-GPRegistryValue -Name "Default Domain Policy" -Key "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Cryptography\AutoEnrollment" -ValueName "OfflineExpirationPercent" -Value 10 -Type "Dword"
Set-GPRegistryValue -Name "Default Domain Policy" -Key "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Cryptography\AutoEnrollment" -ValueName "OfflineExpirationStoreNames" -Value "MY" -Type "String"

gpupdate /force
```

AutoEnrollment should be successfully set up. You can verify it using:

```
Get-CertificateAutoEnrollmentPolicy -Scope Applied -context Machine
```

It should output:

```
PolicyState                : Enabled
EnableMyStoreManagement    : True
EnableTemplateCheck        : True
ExpirationPercentage       : 10
StoreName                  : {MY}
EnableBalloonNotifications : False
```

and

```
Get-GPRegistryValue -Name "Default Domain Policy" -Key "HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Cryptography\AutoEnrollment"
```

### Create Test Computer Certificate Template

**This step needs to be done manually using the Certification Authority
utility.** Certificate templates define how certificate requests should be
generated and what properties they should have. See the [Certificate Templates
section of the Certificate Auto Enrollment Policy guide][cert-templates] for
detailed instructions on creating and configuring a test computer certificate
template.

[cert-templates]: https://dmulder.github.io/group-policy-book/certautoenroll.html#certificate-templates

### Create Test User Certificate Template

**This step needs to be done manually using the Certification Authority
utility.** To test both direct enrollment and enrollment with approval, create
a copy of the default "User" template. Name it "UserManualApprove" and in the
"Issuance Requirements" tab, enable the option "Approval of certificate
authority required". In the "Security" tab, make sure that your users have
the "Enroll" permission and do not forget to enable the newly created template.

An IIS restart (`iisreset`) is needed in order to make the new template available
via CEP/CES.
