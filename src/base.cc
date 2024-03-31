#include "whr.h"
#include <algorithm>
#include <iomanip>
#include <iostream>

namespace whr {
Base::Base(double w2, int virtual_games)
    : w2_(w2), virtual_games_(virtual_games) {}

void Base::print_ordered_ratings() const {
  std::vector<std::shared_ptr<Player>> players;
  for (auto player_it : players_) {
    if (player_it.second->get_days().size() > 0) {
      players.push_back(player_it.second);
    }
  }
  std::sort(
      players.begin(), players.end(),
      [](const std::shared_ptr<Player> p1, const std::shared_ptr<Player> p2) {
        return p1->get_days().back()->gamma() > p2->get_days().back()->gamma();
      });
  for (const auto player : players) {
    std::cout << player->get_name() << "\t";
    const auto player_days = player->get_days();
    for (size_t i = 0; i < player_days.size(); i++) {
      std::cout << player_days[i]->get_time_step() << ",";
      std::cout << std::fixed << std::setprecision(2) << player_days[i]->elo()
                << std::resetiosflags(std::ios::fixed);
      if (i < player_days.size() - 1) {
        std::cout << ";";
      }
    }
    std::cout << std::endl;
  }
}

py::list Base::get_ordered_ratings() {
  py::list res;
  std::vector<std::shared_ptr<Player>> players;
  for (auto player_it : players_) {
    if (player_it.second->get_days().size() > 0) {
      players.push_back(player_it.second);
    }
  }
  std::sort(
      players.begin(), players.end(),
      [](const std::shared_ptr<Player> &p1, const std::shared_ptr<Player> &p2) {
        return p1->get_days().back()->gamma() > p2->get_days().back()->gamma();
      });
  for (const auto player : players) {
    py::tuple player_ratings(2);
    player_ratings[0] = player->get_name();
    player_ratings[1] = ratings_for_player(player->get_name());
    res.append(player_ratings);
  }
  return res;
}

double Base::log_likelihood() const {
  double score = 0.;
  for (const auto player_it : players_) {
    if (player_it.second->get_days().size() > 0) {
      score += player_it.second->log_likelihood();
    }
  }
  return score;
}

std::shared_ptr<Player> Base::player_by_name(std::string name) {
  if (players_.find(name) == players_.end()) {
    players_[name] = std::make_shared<Player>(name, w2_, virtual_games_);
    players_order_.push_back(name);
  }
  return players_[name];
}

py::list Base::ratings_for_player(std::string name) {
  py::list res;
  auto player = player_by_name(name);
  for (const auto d : player->get_days()) {
    py::list pd_info;
    pd_info.append(d->get_time_step());
    pd_info.append(d->elo());
    pd_info.append(std::sqrt(d->get_uncertainty()) * 400. / std::log(10.));
    res.append(pd_info);
  }
  return res;
}

std::shared_ptr<Game> Base::setup_game(std::string black, std::string white,
                                       std::string winner, int time_step,
                                       double handicap) {
  if (black == white) {
    std::cerr << "Game players cannot be equal: " << black << " and " << white
              << std::endl;
    return nullptr;
  }
  std::shared_ptr<Player> white_player = player_by_name(white);
  std::shared_ptr<Player> black_player = player_by_name(black);
  std::shared_ptr<Game> game = std::make_shared<Game>(
      black_player, white_player, winner, time_step, handicap);
  return game;
}

void Base::create_games(const py::list games) {
  std::vector<py::list> games_list;
  for (size_t i = 0; i < games.size(); i++) {
    games_list.push_back(games[i]);
  }
  std::sort(games_list.begin(), games_list.end(),
            [](const py::list g1, const py::list g2) { return g1[3] < g2[3]; });
  for (const py::list game : games_list) {
    std::string black = py::cast<std::string>(game[0]);
    std::string white = py::cast<std::string>(game[1]);
    std::string winner = py::cast<std::string>(game[2]);
    int time_step = py::cast<int>(game[3]);
    double handicap = 0.;
    if (game.size() >= 5) {
      handicap = py::cast<double>(game[4]);
    }
    create_game(black, white, winner, time_step, handicap);
  }
}

void Base::create_game(std::string black, std::string white, std::string winner,
                       int time_step, double handicap) {
  std::shared_ptr<Game> game =
      setup_game(black, white, winner, time_step, handicap);
  if (game != nullptr) {
    add_game(game);
  }
}

void Base::add_game(const std::shared_ptr<Game> game) {
  games_.push_back(game);
  game->get_white_player()->add_game(game);
  game->get_black_player()->add_game(game);
}

int Base::iterate_until_coverge(bool verbose) {
  int count = 0;
  std::vector<int> ratings, last_ratings;
  int best_iteration;
  std::vector<std::pair<std::string, std::shared_ptr<Player>>> sorted_players;
  sorted_players.reserve(players_.size());
  std::copy(players_.begin(), players_.end(),
            std::back_inserter(sorted_players));
  std::sort(sorted_players.begin(), sorted_players.end(),
            [](const std::pair<std::string, std::shared_ptr<Player>> &p1,
               const std::pair<std::string, std::shared_ptr<Player>> &p2) {
              return p1.first < p2.first;
            });
  while (true) {
    ratings.clear();
    for (const auto &player : sorted_players) {
      for (const auto day : player.second->get_days()) {
        ratings.push_back(static_cast<int>(std::round(day->elo() * 100.)));
      }
    }
    int delta = 0;
    if (count > 0) {
      for (size_t i = 0; i < ratings.size(); i++) {
        delta += std::abs(ratings[i] - last_ratings[i]);
      }
      if (verbose) {
        std::cout << "Iteration: " << count << ", delta: " << delta
                  << std::endl;
      }
      if (delta > 0) {
        best_iteration = count;
      }
      if (count - best_iteration >= 10) {
        break;
      }
    } else {
      best_iteration = count;
    }
    last_ratings = ratings;
    run_one_iteration();
    count++;
  }
  for (auto &player : players_) {
    player.second->update_uncertainty();
  }
  return count;
}

void Base::iterate(int count) {
  for (int i = 0; i < count; i++) {
    run_one_iteration();
  }
  for (auto &player : players_) {
    player.second->update_uncertainty();
  }
}

void Base::run_one_iteration() {
  for (const std::string &name : players_order_) {
    players_[name]->run_one_newton_iteration();
  }
}

} // namespace whr
