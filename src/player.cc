#include "whr.h"
#include <cmath>
#include <cstdio>
#include <iostream>

namespace whr {

Player::Player(std::string name, double w2, int virtual_games)
    : name_(name), w2_(w2 * std::pow((std::log(10.) / 400.), 2)),
      virtual_games_(virtual_games) {}

std::string Player::inspect() const {
  char buffer[1000];
  std::snprintf(buffer, 1000, "Player:(%s)", name_.c_str());
  return std::string(buffer);
}

double Player::log_likelihood() const {
  double sum = 0.;
  std::vector<double> sigma2;
  compute_sigma2(sigma2);
  size_t n = days_.size();
  for (size_t i = 0; i < n; i++) {
    double prior = 0.;
    if (i < n - 1) {
      double rd = days_[i]->get_r() - days_[i + 1]->get_r();
      prior +=
          std::exp(-rd * rd / 2. / sigma2[i]) / std::sqrt(2. * PI * sigma2[i]);
    }
    if (i > 0) {
      double rd = days_[i]->get_r() - days_[i - 1]->get_r();
      prior += std::exp(-rd * rd / 2. / sigma2[i - 1]) /
               std::sqrt(2 * PI * sigma2[i - 1]);
    }
    if (prior == 0.) {
      sum += days_[i]->log_likelihood();
    } else {
      double likelihood = days_[i]->log_likelihood();
      double log_prior = std::log(prior);
      sum += likelihood + log_prior;
    }
  }
  return sum;
}

void Player::hessian(const std::vector<double> &sigma2,
                     std::vector<double> &res) const {
  size_t n = days_.size();
  res = std::vector<double>(n * n, 0.);
  for (size_t row = 0; row < n; row++) {
    for (size_t col = 0; col < n; col++) {
      if (row == col) {
        double prior = 0.;
        if (row < n - 1) {
          prior += -1. / sigma2[row];
        }
        if (row > 0) {
          prior += -1. / sigma2[row - 1];
        }
        res[row * n + col] =
            days_[row]->log_likelihood_second_derivative() + prior - 0.001;
      } else if (row == col - 1) {
        res[row * n + col] = 1. / sigma2[row];
      } else if (row == col + 1) {
        res[row * n + col] = 1. / sigma2[col];
      }
    }
  }
}

void Player::gradient(const std::vector<double> &r,
                      const std::vector<double> &sigma2,
                      std::vector<double> &res) const {
  size_t n = days_.size();
  res = std::vector<double>(n, 0.);
  for (size_t i = 0; i < n; i++) {
    auto day = days_[i];
    double prior = 0.;
    if (i < n - 1) {
      prior += -(r[i] - r[i + 1]) / sigma2[i];
    }
    if (i > 0) {
      prior += -(r[i] - r[i - 1]) / sigma2[i - 1];
    }
    res[i] = day->log_likelihood_derivative() + prior;
  }
}

void Player::run_one_newton_iteration() {
  for (auto day : days_) {
    day->clear_game_terms_cache();
  }
  if (days_.size() == 1) {
    days_[0]->update_by_1d_newtons_method();
  } else if (days_.size() > 1) {
    update_by_ndim_newton();
  }
}

void Player::compute_sigma2(std::vector<double> &res) const {
  size_t n = days_.size();
  res = std::vector<double>(n - 1, 0.);
  for (size_t i = 0; i < n - 1; i++) {
    auto d1 = days_[i];
    auto d2 = days_[i + 1];
    res[i] = std::abs(d2->get_time_step() - d1->get_time_step()) * w2_;
  }
}

void Player::update_by_ndim_newton() {
  size_t n = days_.size();
  std::vector<double> r(n);
  for (size_t i = 0; i < n; i++) {
    r[i] = days_[i]->get_r();
  }
  std::vector<double> sigma2, h, g;
  compute_sigma2(sigma2);
  hessian(sigma2, h);
  gradient(r, sigma2, g);
  std::vector<double> a(n, 0.), d(n, 0.), b(n, 0.), y(n, 0.), x(n, 0.);
  d[0] = h[0];
  b[0] = h[1];
  for (size_t i = 1; i < n; i++) {
    a[i] = h[i * n + i - 1] / d[i - 1];
    d[i] = h[i * n + i] - a[i] * b[i - 1];
    if (i < n - 1) {
      b[i] = h[i * n + i + 1];
    }
  }
  y[0] = g[0];
  for (size_t i = 1; i < n; i++) {
    y[i] = g[i] - a[i] * y[i - 1];
  }
  x[n - 1] = y[n - 1] / d[n - 1];
  for (int i = static_cast<int>(n) - 2; i >= 0; i--) {
    x[i] = (y[i] - b[i] * x[i + 1]) / d[i];
  }
  for (size_t i = 0; i < n; i++) {
    days_[i]->set_r(r[i] - x[i]);
  }
}

void Player::covariance(std::vector<double> &res) const {
  size_t n = days_.size();
  std::vector<double> sigma2, h;
  compute_sigma2(sigma2);
  hessian(sigma2, h);
  std::vector<double> a(n, 0.), d(n, 0.), b(n, 0.);
  d[0] = h[0];
  if (n > 1) {
    b[0] = h[1];
  }
  for (size_t i = 1; i < n; i++) {
    a[i] = h[i * n + i - 1] / d[i - 1];
    d[i] = h[i * n + i] - a[i] * b[i - 1];
    if (i < n - 1) {
      b[i] = h[i * n + i + 1];
    }
  }
  std::vector<double> dp(n, 0.), bp(n, 0.), ap(n, 0.);
  dp[n - 1] = h[n * n - 1];
  bp[n - 1] = h[n * n - 2];
  for (int i = static_cast<int>(n) - 2; i >= 0; i--) {
    ap[i] = h[i * n + i + 1] / dp[i + 1];
    dp[i] = h[i * n + i] - ap[i] * bp[i + 1];
    bp[i] = h[i * n + i - 1];
  }
  std::vector<double> v(n, 0.);
  for (size_t i = 0; i < n - 1; i++) {
    v[i] = dp[i + 1] / (b[i] * bp[i + 1] - d[i] * dp[i + 1]);
  }
  v[n - 1] = -1. / d[n - 1];
  res = std::vector<double>(n * n, 0.);
  for (size_t row = 0; row < n; row++) {
    for (size_t col = 0; col < n; col++) {
      if (row == col) {
        res[row * n + col] = v[row];
      } else if (row == col - 1) {
        res[row * n + col] = -a[col] * v[col];
      }
    }
  }
}

void Player::update_uncertainty() {
  size_t n = days_.size();
  if (n > 0) {
    std::vector<double> c;
    covariance(c);
    for (size_t i = 0; i < n; i++) {
      days_[i]->set_uncertainty(c[i * n + i]);
    }
  }
}

void Player::add_game(std::shared_ptr<Game> game) {
  size_t n = days_.size();
  if (n == 0 || days_[n - 1]->get_time_step() != game->get_time_step()) {
    auto new_pday =
        std::make_shared<PlayerDay>(shared_from_this(), game->get_time_step());
    if (n == 0) {
      new_pday->set_is_first_day(true);
      new_pday->set_gamma(1.);
    } else {
      new_pday->set_gamma(days_[n - 1]->gamma());
    }
    days_.push_back(new_pday);
  }
  n = days_.size();
  if (game->get_white_player() == shared_from_this()) {
    game->set_wpd(days_[n - 1]);
  } else {
    game->set_bpd(days_[n - 1]);
  }
  days_[n - 1]->add_game(game);
}

} // namespace whr
