data {
  int<lower=1> N;                                 // number of observations
  int<lower=1> num_precincts;                     // number of precincts
  int<lower=1,upper=num_precincts> precinct[N];   // precinct for each observation
  int<lower=1,upper=42> hourgroup[N];             // hourgroup for each observation

  real<lower=0> gamma_scale;                      // affects the prior
  
  int<lower=0> y[N];                              // data
}
parameters {
  real beta_0;
  vector[num_precincts] beta_precinct;            
  vector[42] beta_hourgroup;
  matrix<lower=0>[num_precincts, 42] lambda;
}
transformed parameters {
  matrix[num_precincts, 42] mu;
  for (p in 1:num_precincts) {
    for (h in 1:42) {
      mu[p, h] = exp(beta_0 + beta_precinct[p] + beta_hourgroup[h]);
    }
  }
}
model {
  beta_0 ~ student_t(3, 0, 1);
  beta_precinct ~ student_t(3, 0, 1);
  beta_hourgroup ~ student_t(3, 0, 1);
  for (p in 1:num_precincts) {
    for (h in 1:42) {
      lambda[p, h] ~ gamma(mu[p, h]/gamma_scale, 1/gamma_scale);
    }
  }
  for (n in 1:N) {
    y[n] ~ poisson(lambda[precinct[n], hourgroup[n]]);
  }
}

