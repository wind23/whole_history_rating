#include "whr.h"
#include <pybind11/pybind11.h>

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

namespace py = pybind11;

PYBIND11_MODULE(whr_core, m) {
  py::class_<whr::Base>(m, "Base")
      .def(py::init<double, int>(), py::arg("w2") = 300.,
           py::arg("virtual_games") = 2)
      .def("print_ordered_ratings", &whr::Base::print_ordered_ratings)
      .def("get_ordered_ratings", &whr::Base::get_ordered_ratings)
      .def("log_likelihood", &whr::Base::log_likelihood)
      .def("ratings_for_player", &whr::Base::ratings_for_player,
           py::arg("name"))
      .def("create_games", &whr::Base::create_games, py::arg("games"))
      .def("create_game", &whr::Base::create_game, py::arg("black"),
           py::arg("white"), py::arg("winner"), py::arg("time_step"),
           py::arg("handicap") = 0.)
      .def("iterate_until_converge", &whr::Base::iterate_until_coverge,
           py::arg("verbose") = true)
      .def("iterate", &whr::Base::iterate, py::arg("count"));

  py::class_<whr::Evaluate>(m, "Evaluate")
      .def(py::init<whr::Base &>(), py::arg("base"))
      .def("get_rating", &whr::Evaluate::get_rating, py::arg("name"),
           py::arg("time_step"), py::arg("ignore_null_players") = true)
      .def("evaluate_ave_log_likelihood_games",
           &whr::Evaluate::evaluate_ave_log_likelihood_games, py::arg("games"),
           py::arg("ignore_null_players") = true);

#ifdef VERSION_INFO
  m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
  m.attr("__version__") = "dev";
#endif
}
