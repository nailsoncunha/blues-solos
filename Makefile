
#INCDIR		= -I ./src/include -I /opt/ibm/ILOG/CPLEX_Studio125/cplex/include/ -I /opt/ibm/ILOG/CPLEX_Studio125/concert/include/
INCDIR		= -I ./src/include -I /opt/ibm/ILOG/CPLEX_Studio124/cplex/include/ -I /opt/ibm/ILOG/CPLEX_Studio124/concert/include/
SRCDIR 		= ./src
BINDIR 		= ./bin
OBJDIR 		= ./obj

CC     		= g++

OPT    		= -O3
OTHER  		= -g -Wall -DIL_STD -lstdc++
LIB_DIR		= -L /opt/ibm/ILOG/CPLEX_Studio124/cplex/lib/x86-64_sles10_4.1/static_pic/ -L /opt/ibm/ILOG/CPLEX_Studio124/concert/lib/x86-64_sles10_4.1/static_pic/
#LIB_DIR		= -L /opt/ibm/ILOG/CPLEX_Studio125/cplex/lib/x86_sles10_4.1/static_pic/ -L /opt/ibm/ILOG/CPLEX_Studio125/concert/lib/x86_sles10_4.1/static_pic/
EXTRA_LIBS 	= -pthread -lm -lilocplex -lcplex -lconcert
DEBUG		= 
OK 			= \033[30;32mOK!\033[m

#-----------------------------------------------------


SOURCES =	byRoutingFlow.cpp \
			byScheduling.cpp \
            tools.cpp \
#            MyCutCallbackMinCut.cpp \
#            input.cpp \
#            ils.cpp \

# Main Sources
MSOURCES =  main_byRoutingFlow.cpp \
			main_byScheduling.cpp \
			main_subtour.cpp \
#			main_ils.cpp \
#			main_grasp.cpp \

MCCMC 	=	$(OBJDIR)/MyCutCallbackMinCut.o


MAIN_BYRFLOW	= $(OBJDIR)/main_byRoutingFlow.o
MAIN_BYSCHED	= $(OBJDIR)/main_byScheduling.o
MAIN_SUBTOUR	= $(OBJDIR)/main_subtour.o
#MAIN_ILS 		= $(OBJDIR)/main_ils.o
#MAIN_GRASP 		= $(OBJDIR)/main_grasp.o

LIBS 			=  $(LIB_DIR) $(EXTRA_LIBS)
SRCS			=  $(addprefix $(SRCDIR)/,$(SOURCES))
MSRCS			=  $(addprefix $(SRCDIR)/,$(MSOURCES))

HEADERS 		:= $(foreach dir,$(INCDIR),$(wildcard $(dir)/*.h))

BYSCHED			=  $(BINDIR)/byScheduling
BYRFLOW			=  $(BINDIR)/byRoutingFlow
SUBTOUR			=  $(BINDIR)/bySubtour
#GRASP			=  $(BINDIR)/grasp


OBJS 			=  $(addprefix $(OBJDIR)/,$(SOURCES:.cpp=.o))
MOBJS 			=  $(addprefix $(OBJDIR)/,$(MSOURCES:.cpp=.o))
CFLAGS 			=  $(DEBUG) $(OTHER) $(OPT) $(INCDIR)


.SUFFIXES: .cpp .o .h

# ALL -------------------------------------------------------------------
all: $(BYSCHED) $(BYRFLOW) $(SUBTOUR)

# BYSCHED -----------------------------------------------------------------
$(BYSCHED): $(OBJS) $(MAIN_BYSCHED)
	@mkdir $(BINDIR) > /dev/null 2>&1 && echo "Criando diretorio $(BINDIR)... $(OK)" || echo -n""
	@echo -n Linkando $(notdir $(BYSCHED))... 
	@$(CC) $(CFLAGS) $(LIBDIR) -o $@ $(MAIN_BYSCHED) $(OBJS) $(LIBS) && echo " $(OK)"

# BYRFLOW -----------------------------------------------------------------
$(BYRFLOW): $(OBJS) $(MAIN_BYRFLOW)
	@mkdir $(BINDIR) > /dev/null 2>&1 && echo "Criando diretorio $(BINDIR)... $(OK)" || echo -n""
	@echo -n Linkando $(notdir $(BYRFLOW))... 
	@$(CC) $(CFLAGS) $(LIBDIR) -o $@ $(MAIN_BYRFLOW) $(OBJS) $(LIBS) && echo " $(OK)"

# SUBTOUR -----------------------------------------------------------------
$(SUBTOUR): $(OBJS) $(MAIN_SUBTOUR) $(MCCMC)
	@mkdir $(BINDIR) > /dev/null 2>&1 && echo "Criando diretorio $(BINDIR)... $(OK)" || echo -n""
	@echo -n Linkando $(notdir $(SUBTOUR))... 
	@$(CC) $(CFLAGS) $(LIBDIR) -o $@ $(MAIN_SUBTOUR) $(MCCMC) $(OBJS) $(LIBS) && echo " $(OK)"

# GRASP -----------------------------------------------------------------
#$(GRASP): $(OBJS) $(MAIN_GRASP) $(DEPS)
#	@mkdir $(BINDIR) > /dev/null 2>&1 && echo "Criando diretorio $(BINDIR)... $(OK)" || echo -n""
#	@echo -n Linkando $(notdir $(GRASP))... 
#	@$(CC) $(CFLAGS) $(LIBDIR) -o $@ $(MAIN_GRASP) $(OBJS) $(LIBS) && echo " $(OK)"

%.o: ../src/%.cpp
	@echo -n Compilando arquivo $(notdir $<) para $(notdir $@)... 
	@$(CC) $(OTHER) $(CFLAGS) -c $< -o obj/$(notdir $@) && echo -e " $(OK)"

	
re: clean all

clean::
	@echo -n Limpando o lixo... 
	@rm -rf ./bin 2> /dev/null
	@find -iname "*.o" -exec rm {} \; 2> /dev/null
	@find -iname "*~" -exec rm {} \; 2> /dev/null
	@echo " $(OK)"

print: src/*.cpp include/*.h
	@echo " $(subst \ ,\n,$?)"

