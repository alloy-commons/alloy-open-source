variable "name" {
  type        = string
  description = "Name for the various cognito resources"
}

variable "dns_name" {
  type        = string
  description = "DNS name for the authenticate page (e.g. `auth.my-company.com`)"
}

variable "zone_id" {
  type        = string
  description = "Route53 zone id to put DNS records in"
}

variable "saml_metadata_file_content" {
  type        = string
  description = "Contents of the SAML metadata file"
}

variable "saml_metadata_sso_redirect_binding_uri" {
  type        = string
  description = "The HTTP-Redirect SSO binding from the SAML metadata file. Must be kept in sync with saml_metadata_file_content!"
}

variable "relying_party_dns_names" {
  type        = list(string)
  description = "List of DNS names for the relying parties (i.e. the applications you are authenticating with this)"
}
