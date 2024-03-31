
#include <memory>
#include <pybind11/pybind11.h>
#include <string>
#include <unordered_map>
#include <vector>

namespace py = pybind11;

namespace whr {
const double PI = 3.14159265358979323846;

enum class Winner { WHITE, BLACK, DRAW };

class Game;
class PlayerDay;

class GameTerm {
public:
  double a, b, c, d;
  GameTerm(double a, double b, double c, double d) : a(a), b(b), c(c), d(d) {}
};

class EvaluateGame {
public:
  int time_step;
  std::string white_player;
  std::string black_player;
  Winner winner;
  double handicap;
  EvaluateGame(std::string black_player, std::string white_player,
               std::string winner, int time_step, double handicap = 0.)
      : black_player(black_player), white_player(white_player),
        winner(winner == "W" ? Winner::WHITE
                             : (winner == "B" ? Winner::BLACK : Winner::DRAW)),
        time_step(time_step), handicap(handicap) {}
};

class Player : public std::enable_shared_from_this<Player> {
  std::string name_;
  double w2_;
  int virtual_games_;
  std::vector<std::shared_ptr<PlayerDay>> days_;
  std::string inspect() const;
  void hessian(const std::vector<double> &sigma2,
               std::vector<double> &res) const;
  void gradient(const std::vector<double> &r, const std::vector<double> &sigma2,
                std::vector<double> &res) const;
  void compute_sigma2(std::vector<double> &res) const;
  void update_by_ndim_newton();
  void covariance(std::vector<double> &res) const;

public:
  Player(std::string name, double w2, int virtual_games);
  std::string get_name() const { return name_; }
  const std::vector<std::shared_ptr<PlayerDay>> &get_days() const {
    return days_;
  }
  int get_virtual_games() const { return virtual_games_; }
  double log_likelihood() const;
  void run_one_newton_iteration();
  void update_uncertainty();
  void add_game(std::shared_ptr<Game> game);
};

class PlayerDay {
  std::shared_ptr<Player> player_;
  int time_step_;
  bool is_first_day_;
  double r_;
  double uncertainty_;
  std::vector<std::shared_ptr<Game>> won_games_;
  std::vector<std::shared_ptr<Game>> draw_games_;
  std::vector<std::shared_ptr<Game>> lost_games_;
  std::vector<GameTerm> won_game_terms_cache_;
  std::vector<GameTerm> draw_game_terms_cache_;
  std::vector<GameTerm> lost_game_terms_cache_;
  bool won_game_terms_cache_initialized_;
  bool draw_game_terms_cache_initialized_;
  bool lost_game_terms_cache_initialized_;

  void compute_won_game_terms();
  void compute_draw_game_terms();
  void compute_lost_game_terms();
  void compute_game_terms();

public:
  PlayerDay(const std::shared_ptr<Player> player, int time_step);
  double get_r() const { return r_; }
  void set_r(double r) { r_ = r; }
  int get_time_step() const { return time_step_; }
  double get_uncertainty() const { return uncertainty_; }
  void set_uncertainty(double undertainty) { uncertainty_ = undertainty; }
  void set_is_first_day(bool is_first_day) { is_first_day_ = is_first_day; }
  void set_gamma(double gamma);
  double gamma() const;
  void set_elo(double elo);
  double elo() const;
  double log_likelihood_second_derivative();
  double log_likelihood_derivative();
  double log_likelihood();
  void clear_game_terms_cache();
  void add_game(const std::shared_ptr<Game> game);
  void update_by_1d_newtons_method();
};

class Game {
  int time_step_;
  std::shared_ptr<Player> white_player_;
  std::shared_ptr<Player> black_player_;
  Winner winner_;
  double handicap_;
  std::shared_ptr<PlayerDay> wpd_;
  std::shared_ptr<PlayerDay> bpd_;

  std::string inspect();
  std::shared_ptr<Player> opponent(const std::shared_ptr<Player> player);
  double likelihood();
  double white_win_probability();
  double black_win_probability();

public:
  Game(const std::shared_ptr<Player> black, const std::shared_ptr<Player> white,
       std::string winner, int time_step, double handicap = 0.);
  int get_time_step() const { return time_step_; }
  Winner get_winner() const { return winner_; }
  std::shared_ptr<Player> get_white_player() const { return white_player_; }
  std::shared_ptr<Player> get_black_player() const { return black_player_; }
  void set_wpd(const std::shared_ptr<PlayerDay> wpd) { wpd_ = wpd; }
  void set_bpd(const std::shared_ptr<PlayerDay> bpd) { bpd_ = bpd; }
  double opponents_adjusted_gamma(const std::shared_ptr<Player> player) const;
};

class Base {
  double w2_;
  int virtual_games_;
  std::vector<std::shared_ptr<Game>> games_;
  std::unordered_map<std::string, std::shared_ptr<Player>> players_;
  std::vector<std::string> players_order_;
  std::shared_ptr<Player> player_by_name(std::string name);
  std::shared_ptr<Game> setup_game(std::string black, std::string white,
                                   std::string winner, int time_step,
                                   double handicap);
  void add_game(const std::shared_ptr<Game> game);
  void run_one_iteration();

public:
  Base(double w2 = 300., int virtual_games = 2);
  std::unordered_map<std::string, std::shared_ptr<Player>> &get_players() {
    return players_;
  }
  void print_ordered_ratings() const;
  py::list get_ordered_ratings();
  double log_likelihood() const;
  py::list ratings_for_player(std::string name);
  void create_games(const py::list games);
  void create_game(std::string black, std::string white, std::string winner,
                   int time_step, double handicap = 0.);
  int iterate_until_coverge(bool verbose = true);
  void iterate(int count);
};

class Evaluate {
  std::unordered_map<std::string, std::vector<std::pair<int, double>>>
      ratings_by_players_;
  double evaluate_single_game(const EvaluateGame &game,
                              bool ignore_null_players = true) const;
  void list_to_games(const py::list games,
                     std::vector<EvaluateGame> &game_list) const;

public:
  Evaluate(Base &base);
  double get_rating(std::string name, int time_step,
                    bool ignore_null_players = true) const;
  double
  evaluate_ave_log_likelihood_games(const py::list games,
                                    bool ignore_null_players = true) const;
};

} // namespace whr
