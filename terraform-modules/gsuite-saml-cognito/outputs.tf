output "cognito_user_pool_arn" {
  value = aws_cognito_user_pool.gsuite_saml.arn
}

output "cognito_user_pool_client_id" {
  value = aws_cognito_user_pool_client.gsuite_saml.id
}

output "cognito_user_pool_domain" {
  value = var.dns_name
}
