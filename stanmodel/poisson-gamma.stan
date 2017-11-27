data {
  int<lower=0> J; // number of "precincts"
  int<lower=0> N; // number of observations per precinct
  real<lower=0> gamma_scale;

  real exp_var[J]; // explanatory variable
  
  int<lower=0> y[J,N]; // data
}
parameters {
  real beta[2];
  real<lower=0> lambda[J];
}
transformed parameters {
  real<lower=0> mu[J];
  for (j in 1:J) {
    mu[j] = exp(beta[1] + beta[2] * exp_var[j]);
  }
}
model {
  beta ~ student_t(3, 0, 1);
  for (j in 1:J) {
    lambda[j] ~ gamma(mu[j]/gamma_scale, 1/gamma_scale);
    y[j] ~ poisson(lambda[j]);
  }
}

