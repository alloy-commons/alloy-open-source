# `gsuite-saml-cognito`

Provisions AWS Cognito resources for connecting to a GSuite instance SAML
authentication.

This gives you a user pool, user pool client, and user pool domain (using a
custom domain with a certificate and both A and AAAA records), which can be
used with ALB's authentication support.

## Parameters

- `name`: Name for the Cognito resources
- `dns_name`: DNS name for the authentication website
- `zone_id`: Route 53 zone id where DNS records will be placed
- `saml_metadata_file_content`: Contents of the SAML metadata file from the IDP
- `saml_metadata_sso_redirect_binding_uri`: The HTTP-Redirect SSO binding from
  the SAML metadata file. Must be kept in sync with
  `saml_metadata_file_content`!
- `relying_party_dns_names`: List of DNS names for all the services you'll be
  authenticating with this resource.

Also requires a provider named `aws.us-east-1`, which is required for
provisioning an ACM certificate.

## Outputs

- `cognito_user_pool_arn`: ARN for the Cognito User Pool
- `cognito_user_pool_client_id`: ID for the Cognito User Pool Client
- `cognito_user_pool_domain`: Name for the Cognito User Pool Domain

## Example usage

Process wise, you'll need to start creating a SAML App in the GSuite admin,
download the SAML Metadata XML file, then create the Terraform resources, and
then complete creating the SAML App in the GSuite admin. You'll use the
following configuration values in the GSuite admin:

- `ACS URL`: `https://{dns_name}/saml2/idpresponse`
- `Entity ID`: `urn:amazon:cognito:sp:{id}` where `id` is the final component
  of the Cognito User Pool ARN.
- `Name ID Format`: `EMAIL`
- `Attribute Mapping`:
  - Add a value named `email` which maps to `Primary Email`

```hcl
module "gsuite_saml_cognito" {
  source = "../modules/gsuite-saml-cognito"

  name                                   = "GSuiteSAML"
  dns_name                               = "cognito-sso.my-corp.com"
  zone_id                                = aws_route53_zone.my_corp.zone_id
  saml_metadata_file_content             = file("cognito-gsuite-saml-metadata.xml")
  saml_metadata_sso_redirect_binding_uri = "https://accounts.google.com/o/saml2/idp?idpid=<id>"
  relying_party_dns_names                = ["my-app.int.my-corp.com", "my-other-app.int.my-corp.com"]

  providers = {
    aws           = aws
    aws.us-east-1 = aws.us-east-1
  }
}
```

This will leave you with Cognito resources, that use
`https://cognito-sso.my-corp.com` as the domain that is a RP for the GSuite
SAML IDP. It can be used to provide authentication for apps running on the
domains `my-app.int.my-corp.com` and `my-other-app.int.my-corp.com`.
