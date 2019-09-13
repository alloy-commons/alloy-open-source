# Amazon Certificate Manager Terraform Modules

This is a [Terraform](https://www.terraform.io/) module which issues a
certificate with Amazon's Certificate Manager, automatically completing its
verification with Route53 DNS.

## Example usage

```
data "aws_route53_zone" "mydomain" {
  name = "mydomain.com."
}

module "cert" {
  source = "git::https://github.com/alloy-commons/alloy-open-source//terraform-modules/acm"

  domain_names = ["mydomain.com", "sub.mydomain.com"]
  zone_id = data.aws_route53_zone.mydomain.zone_id
}
```

## Variables

- `domain_names`: List of domain names that the certificate should be valid
  for.
- `zone_id`: Route53 hosted zone in which to provision the verification DNS
  records.

## Outputs

- `acm_certificate_arn`: ARN for the ACM certificate that has been provisioned.
