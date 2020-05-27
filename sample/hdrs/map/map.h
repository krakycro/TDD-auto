#ifndef MAP_H
#define MAP_H

#include <string>

namespace map
{

class Map
{
    int a;

  public:
    Map(): a{0} {}

    void Init(int a) { this->a = a; }

    Map(std::string s);

    void Init(std::string s);

    void Init(std::string s, int a) {  this->a = a; }

}; // class Map

} // namespace map

#endif // MAP_H