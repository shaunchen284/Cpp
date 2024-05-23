#include <iostream>
# include <ctime>
using namespace std;




#include "swap.h"

int main() {
    int a = 10;
    a = 20;
    int arr[] = {0,1,2,3,4,5,6,7,8,9};
    int *p = arr;
    for(int i=0;i<10;i++){
       cout<<*p<<endl;
       p++;
    }


    return 0;
}
