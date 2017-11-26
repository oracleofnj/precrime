data {
  int<lower=0> J; // number of precincts
  int<lower=0> N; // number of time bins

  real<lower=0> exp_var[J]; // covariates
  
  int<lower=0> y[J,N]; // number of crimes
}
parameters {
  real beta[2];
  real<lower=0> lambda[J];
}
transformed parameters {
  real lp[J];
  real<lower=0> mu[J];
  for (j in 1:J) {
    lp[j] = beta[1] + beta[2] * exp_var[j];
    mu[j] = exp(lp[j]);
  }
}
model {
  for (j in 1:J) {
    lambda[j] ~ gamma(10 * mu[j], 0.1);
    y[j] ~ poisson(lambda[j]);
  }
}

