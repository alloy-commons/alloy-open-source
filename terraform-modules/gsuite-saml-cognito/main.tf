terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider aws {
}

provider aws {
  alias = "us-east-1"
}

resource "aws_cognito_user_pool" "gsuite_saml" {
  name             = var.name
  alias_attributes = ["email"]

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    // Required to be mutable for any attribute that comes from a SAML IDP.
    mutable = true

    // These are just the defaults, but if you don't include them then you
    // trigger:
    // https://github.com/terraform-providers/terraform-provider-aws/issues/4227
    string_attribute_constraints {
      min_length = 0
      max_length = 2048
    }
  }
}

resource "aws_cognito_user_pool_client" "gsuite_saml" {
  name                         = var.name
  user_pool_id                 = aws_cognito_user_pool.gsuite_saml.id
  supported_identity_providers = [aws_cognito_identity_provider.gsuite_saml.provider_name]
  callback_urls = toset(concat(
    [
      "https://${var.dns_name}",
      "https://${var.dns_name}/oauth2/idpresponse",
      "https://${var.dns_name}/saml2/idpresponse",
    ],
    sort(flatten([for dns_name in var.relying_party_dns_names :
      [
        "https://${dns_name}/",
        "https://${dns_name}/oauth2/idpresponse",
        "https://${dns_name}/saml2/idpresponse",
      ]
    ]))
  ))
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid"]
  generate_secret                      = true
}

module "auth_domain_certificate" {
  source = "git::https://github.com/alloy-commons/alloy-open-source//terraform-modules/acm?ref=5315c4dd18eedf00bb16c3e82ff7e906a74ed63d"

  domain_names = [var.dns_name]
  zone_id      = var.zone_id

  providers = {
    aws = aws.us-east-1
  }
}

resource "aws_cognito_user_pool_domain" "gsuite_saml" {
  domain          = var.dns_name
  user_pool_id    = aws_cognito_user_pool.gsuite_saml.id
  certificate_arn = module.auth_domain_certificate.acm_certificate_arn
}

resource "aws_route53_record" "cognito_auth" {
  name    = var.dns_name
  zone_id = var.zone_id
  type    = "A"

  alias {
    name = aws_cognito_user_pool_domain.gsuite_saml.cloudfront_distribution_arn
    // This is the zone id for CloudFront.
    zone_id                = "Z2FDTNDATAQYW2"
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "cognito_auth_ipv6" {
  name    = var.dns_name
  zone_id = var.zone_id
  type    = "AAAA"

  alias {
    name = aws_cognito_user_pool_domain.gsuite_saml.cloudfront_distribution_arn
    // This is the zone id for CloudFront.
    zone_id                = "Z2FDTNDATAQYW2"
    evaluate_target_health = false
  }
}


resource "aws_cognito_identity_provider" "gsuite_saml" {
  user_pool_id  = aws_cognito_user_pool.gsuite_saml.id
  provider_name = "GSuite"
  provider_type = "SAML"

  provider_details = {
    MetadataFile = var.saml_metadata_file_content
    // AWS actually computes this value automatically from the MetadataFile,
    // but if we don't specify it, terraform always thinks this resource has
    // changed:
    // https://github.com/terraform-providers/terraform-provider-aws/issues/4831
    SSORedirectBindingURI = var.saml_metadata_sso_redirect_binding_uri
  }

  attribute_mapping = {
    email = "email"
  }
}
