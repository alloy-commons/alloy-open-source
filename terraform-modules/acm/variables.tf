variable "domain_names" {
  type        = list(string)
  description = "List of domain names for the certificate"
}

variable "zone_id" {
  description = "Hosted Zone ID for the verification records"
}
