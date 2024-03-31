#include "whr.h"
#include <algorithm>

namespace whr {

Evaluate::Evaluate(Base &base) {
  for (const auto &player : base.get_players()) {
    std::vector<std::pair<int, double>> ratings;
    for (const auto d : player.second->get_days()) {
      ratings.push_back(std::pair<int, double>(d->get_time_step(), d->elo()));
    }
    std::sort(
        ratings.begin(), ratings.end(),
        [](const std::pair<int, double> &r1, const std::pair<int, double> &r2) {
          return r1.first < r2.first;
        });
    ratings_by_players_[player.first] = ratings;
  }
}

double Evaluate::get_rating(std::string name, int time_step,
                            bool ignore_null_players) const {
  int min_time_step = INT32_MIN;
  int max_time_step = INT32_MIN;
  double min_rating = 0., max_rating = 0.;
  if (ratings_by_players_.find(name) == ratings_by_players_.end()) {
    return ignore_null_players ? std::numeric_limits<double>::quiet_NaN() : 0.;
  }
  const std::vector<std::pair<int, double>> &ratings =
      ratings_by_players_.at(name);
  for (const auto &rating : ratings) {
    if (rating.first <= time_step) {
      if (min_time_step == INT32_MIN || rating.first >= min_time_step) {
        min_time_step = rating.first;
        min_rating = rating.second;
      }
    }
    if (rating.first >= time_step) {
      if (max_time_step == INT32_MIN || rating.first <= max_time_step) {
        max_time_step = rating.first;
        max_rating = rating.second;
      }
    }
  }
  if (min_time_step == INT32_MIN) {
    return max_rating;
  }
  if (max_time_step == INT32_MIN) {
    return min_rating;
  }
  if (max_time_step <= min_time_step) {
    return max_rating;
  }
  return ((max_time_step - time_step) * min_rating +
          (time_step - min_time_step) * max_rating) /
         (max_time_step - min_time_step);
}

double Evaluate::evaluate_single_game(const EvaluateGame &game,
                                      bool ignore_null_players) const {
  double black_rating =
      get_rating(game.black_player, game.time_step, ignore_null_players);
  double white_rating =
      get_rating(game.white_player, game.time_step, ignore_null_players);
  if (!std::isfinite(black_rating) || !std::isfinite(white_rating)) {
    return std::numeric_limits<double>::quiet_NaN();
  }
  double black_advantage = game.handicap;
  double white_gamma = std::pow(10., white_rating / 400.);
  double black_adjusted_gamma =
      std::pow(10., (black_rating + black_advantage) / 400.);
  switch (game.winner) {
  case Winner::WHITE:
    return white_gamma / (white_gamma + black_adjusted_gamma);
  case Winner::BLACK:
    return black_adjusted_gamma / (white_gamma + black_adjusted_gamma);
  default:
    return std::sqrt(white_gamma * black_adjusted_gamma) /
           (white_gamma + black_adjusted_gamma);
  }
}

double
Evaluate::evaluate_ave_log_likelihood_games(const py::list games,
                                            bool ignore_null_players) const {
  double sum = 0.;
  std::vector<EvaluateGame> game_list;
  list_to_games(games, game_list);
  int game_count = 0;
  for (const EvaluateGame game : game_list) {
    double game_likelihood = evaluate_single_game(game, ignore_null_players);
    if (std::isfinite(game_likelihood)) {
      sum += std::log(game_likelihood);
      game_count++;
    }
  }
  if (game_count == 0) {
    return 0.;
  }
  return sum / game_count;
}

void Evaluate::list_to_games(const py::list games,
                             std::vector<EvaluateGame> &game_list) const {
  game_list.clear();
  for (size_t i = 0; i < games.size(); i++) {
    py::list game = games[i];
    std::string black_player = py::cast<std::string>(game[0]);
    std::string white_player = py::cast<std::string>(game[1]);
    std::string winner = py::cast<std::string>(game[2]);
    int time_step = py::cast<int>(game[3]);
    double handicap = 0.;
    if (game.size() >= 5) {
      handicap = py::cast<double>(game[4]);
    }
    game_list.push_back(
        EvaluateGame(black_player, white_player, winner, time_step, handicap));
  }
}

} // namespace whr
