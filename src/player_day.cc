#include "whr.h"
#include <cmath>
#include <iostream>
#include <memory>

namespace whr {

PlayerDay::PlayerDay(const std::shared_ptr<Player> player, int time_step)
    : player_(player), time_step_(time_step), is_first_day_(false),
      won_game_terms_cache_initialized_(false),
      draw_game_terms_cache_initialized_(false),
      lost_game_terms_cache_initialized_(false), r_(0.), uncertainty_(0.) {}

void PlayerDay::set_gamma(double gamma) { r_ = std::log(gamma); }

double PlayerDay::gamma() const { return std::exp(r_); }

void PlayerDay::set_elo(double elo) { r_ = elo * (std::log(10.) / 400.); }

double PlayerDay::elo() const { return r_ * (400. / std::log(10.)); }

void PlayerDay::clear_game_terms_cache() {
  won_game_terms_cache_.clear();
  draw_game_terms_cache_.clear();
  lost_game_terms_cache_.clear();
  won_game_terms_cache_initialized_ = false;
  draw_game_terms_cache_initialized_ = false;
  lost_game_terms_cache_initialized_ = false;
}

void PlayerDay::compute_won_game_terms() {
  if (!won_game_terms_cache_initialized_) {
    won_game_terms_cache_initialized_ = true;
    won_game_terms_cache_.clear();
    for (auto g : won_games_) {
      double other_gamma = g->opponents_adjusted_gamma(player_);
      won_game_terms_cache_.push_back(GameTerm(1., 0., 1., other_gamma));
    }
  }
}

void PlayerDay::compute_draw_game_terms() {
  if (!draw_game_terms_cache_initialized_) {
    draw_game_terms_cache_initialized_ = true;
    draw_game_terms_cache_.clear();
    for (auto g : draw_games_) {
      double other_gamma = g->opponents_adjusted_gamma(player_);
      draw_game_terms_cache_.push_back(
          GameTerm(0.5, 0.5 * other_gamma, 1., other_gamma));
    }
    if (is_first_day_) {
      for (int i = 0; i < player_->get_virtual_games(); i++) {
        draw_game_terms_cache_.push_back(GameTerm(0.5, 0.5, 1., 1.));
      }
    }
  }
}

void PlayerDay::compute_lost_game_terms() {
  if (!lost_game_terms_cache_initialized_) {
    lost_game_terms_cache_initialized_ = true;
    lost_game_terms_cache_.clear();
    for (auto g : lost_games_) {
      double other_gamma = g->opponents_adjusted_gamma(player_);
      lost_game_terms_cache_.push_back(
          GameTerm(0., other_gamma, 1., other_gamma));
    }
  }
}

void PlayerDay::compute_game_terms() {
  compute_won_game_terms();
  compute_draw_game_terms();
  compute_lost_game_terms();
}

double PlayerDay::log_likelihood_second_derivative() {
  double sum = 0.;
  double gamma_this = gamma();
  compute_game_terms();
  for (const auto &terms : {won_game_terms_cache_, draw_game_terms_cache_,
                            lost_game_terms_cache_}) {
    for (const GameTerm &term : terms) {
      sum += (term.c * term.d) / std::pow((term.c * gamma_this + term.d), 2);
    }
  }
  return -gamma_this * sum;
}

double PlayerDay::log_likelihood_derivative() {
  double tally = 0.;
  double gamma_this = gamma();
  compute_game_terms();
  for (const auto &terms : {won_game_terms_cache_, draw_game_terms_cache_,
                            lost_game_terms_cache_}) {
    for (const GameTerm &term : terms) {
      tally += term.c / (term.c * gamma_this + term.d);
    }
  }
  return won_game_terms_cache_.size() + 0.5 * draw_game_terms_cache_.size() -
         gamma_this * tally;
}

double PlayerDay::log_likelihood() {
  double tally = 0.;
  double gamma_this = gamma();
  compute_game_terms();
  for (const GameTerm &term : won_game_terms_cache_) {
    tally += std::log(term.a * gamma_this);
    tally -= std::log(term.c * gamma_this + term.d);
  }
  for (const GameTerm &term : draw_game_terms_cache_) {
    tally += std::log(term.a * 2. * gamma_this) * 0.5;
    tally += std::log(term.b * 2.) * 0.5;
    tally -= std::log(term.c * gamma_this + term.d);
  }
  for (const GameTerm &term : lost_game_terms_cache_) {
    tally += std::log(term.b);
    tally -= std::log(term.c * gamma_this + term.d);
  }
  return tally;
}

void PlayerDay::add_game(const std::shared_ptr<Game> game) {
  if (game->get_winner() == Winner::DRAW) {
    draw_games_.push_back(game);
  } else if ((game->get_winner() == Winner::WHITE &&
              game->get_white_player() == player_) ||
             (game->get_winner() == Winner::BLACK &&
              game->get_black_player() == player_)) {
    won_games_.push_back(game);
  } else {
    lost_games_.push_back(game);
  }
}

void PlayerDay::update_by_1d_newtons_method() {
  double dlogp = log_likelihood_derivative();
  double d2logp = log_likelihood_second_derivative();
  r_ -= dlogp / d2logp;
}

} // namespace whr
